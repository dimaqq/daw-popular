# From https://raw.githubusercontent.com/njsmith/h11/master/examples/curio-server.py
import logging
from socket import SHUT_WR
from wsgiref.handlers import format_date_time

import curio
import h11

MAX_RECV = 2 ** 16
TIMEOUT = 10


class CurioHTTPWrapper:
    def __init__(self, sock):
        self.sock = sock
        self.conn = h11.Connection(h11.SERVER)

    def __str__(self):
        # TODO proper implementation, for now just short name for debugging
        return str(id(self) % 100)

    async def send(self, event):
        # The code below doesn't send ConnectionClosed, so we don't bother
        # handling it here either -- it would require that we do something
        # appropriate when 'data' is None.
        assert type(event) is not h11.ConnectionClosed
        data = self.conn.send(event)
        await self.sock.sendall(data)

    async def _read_from_peer(self):
        if self.conn.they_are_waiting_for_100_continue:
            self.info("Sending 100 Continue")
            go_ahead = h11.InformationalResponse(
                status_code=100,
                headers=self.basic_headers())
            await self.send(go_ahead)
        try:
            data = await self.sock.recv(MAX_RECV)
        except ConnectionError:
            # They've stopped listening. Not much we can do about it here.
            data = b""
        self.conn.receive_data(data)

    async def next_event(self):
        while True:
            event = self.conn.next_event()
            if event is h11.NEED_DATA:
                await self._read_from_peer()
                continue
            return event

    async def shutdown_and_clean_up(self):
        # When this method is called, it's because we definitely want to kill
        # this connection, either as a clean shutdown or because of some kind
        # of error or loss-of-sync bug, and we no longer care if that violates
        # the protocol or not. So we ignore the state of self.conn, and just
        # go ahead and do the shutdown on the socket directly. (If you're
        # implementing a client you might prefer to send ConnectionClosed()
        # and let it raise an exception if that violates the protocol.)
        #
        # Curio bug: doesn't expose shutdown()
        with self.sock.blocking() as real_sock:
            try:
                real_sock.shutdown(SHUT_WR)
            except OSError:
                # They're already gone, nothing to do
                return
        # Wait and read for a bit to give them a chance to see that we closed
        # things, but eventually give up and just close the socket.
        # XX FIXME: possibly we should set SO_LINGER to 0 here, so
        # that in the case where the client has ignored our shutdown and
        # declined to initiate the close themselves, we do a violent shutdown
        # (RST) and avoid the TIME_WAIT?
        # it looks like nginx never does this for keepalive timeouts, and only
        # does it for regular timeouts (slow clients I guess?) if explicitly
        # enabled ("Default: reset_timedout_connection off")
        async with curio.ignore_after(TIMEOUT):
            try:
                while True:
                    # Attempt to read until EOF
                    got = await self.sock.recv(MAX_RECV)
                    if not got:
                        break
            finally:
                await self.sock.close()

    def basic_headers(self):
        # HTTP requires these headers in all responses (client would do
        # something different here)
        return [
            ("Date", format_date_time(None).encode("ascii")),
            ("Server", "Curio/h11")
        ]

    def info(self, *args):
        logging.info("%s: %s", self, args)


async def http_serve(sock, addr):
    wrapper = CurioHTTPWrapper(sock)
    while True:
        assert wrapper.conn.states == {
            h11.CLIENT: h11.IDLE, h11.SERVER: h11.IDLE}

        try:
            async with curio.timeout_after(TIMEOUT):
                # wrapper.info("Server main loop waiting for request")
                event = await wrapper.next_event()
                # wrapper.info(event)
                if type(event) is h11.Request:
                    wrapper.info(event.target)
                    await send_echo_response(wrapper, event)
        except Exception as exc:
            wrapper.info("Error during response handler:", exc)
            await maybe_send_error_response(wrapper, exc)

        if wrapper.conn.our_state is h11.MUST_CLOSE:
            wrapper.info("connection is not reusable, so shutting down")
            await wrapper.shutdown_and_clean_up()
            return
        else:
            try:
                # wrapper.info("trying to re-use connection")
                wrapper.conn.start_next_cycle()
            except h11.ProtocolError:
                states = wrapper.conn.states
                wrapper.info("unexpected state", states, "-- bailing out")
                await maybe_send_error_response(
                    wrapper,
                    RuntimeError("unexpected state {}".format(states)))
                await wrapper.shutdown_and_clean_up()
                return


# Helper function
async def send_simple_response(wrapper, status_code, content_type, body):
    wrapper.info("Sending", status_code,
                 "response with", len(body), "bytes")
    headers = wrapper.basic_headers()
    headers.append(("Content-Type", content_type))
    headers.append(("Content-Length", str(len(body))))
    res = h11.Response(status_code=status_code, headers=headers)
    await wrapper.send(res)
    await wrapper.send(h11.Data(data=body))
    await wrapper.send(h11.EndOfMessage())


async def maybe_send_error_response(wrapper, exc):
    # If we can't send an error, oh well, nothing to be done
    wrapper.info("trying to send error response...")
    if wrapper.conn.our_state not in {h11.IDLE, h11.SEND_RESPONSE}:
        wrapper.info("...but I can't, because our state is",
                     wrapper.conn.our_state)
        return
    try:
        if isinstance(exc, h11.RemoteProtocolError):
            status_code = exc.error_status_hint
        else:
            status_code = 500
        body = str(exc).encode("utf-8")
        await send_simple_response(wrapper,
                                   status_code,
                                   "text/plain; charset=utf-8",
                                   body)
    except Exception as exc:
        wrapper.info("error while sending error response:", exc)


async def send_echo_response(wrapper, request):
    # wrapper.info("Preparing echo response")
    if request.method not in {b"GET", b"POST"}:
        # Laziness: we should send a proper 405 Method Not Allowed with the
        # appropriate Accept: header, but we don't.
        raise RuntimeError("unsupported method")
    body = ""
    while True:
        event = await wrapper.next_event()
        if type(event) is h11.EndOfMessage:
            break
        assert type(event) is h11.Data
        body += event.data.decode("ascii")
    response_body_unicode = str([request.method, request.target, request.headers, body])
    response_body_bytes = response_body_unicode.encode("utf-8")
    await send_simple_response(wrapper,
                               200,
                               "application/json; charset=utf-8",
                               response_body_bytes)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    kernel = curio.Kernel()
    print("Listening on http://localhost:8080")
    kernel.run(curio.tcp_server("localhost", 8080, http_serve))
