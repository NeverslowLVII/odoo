import asyncio
from aiosmtpd.controller import Controller

class Handler:
    async def handle_DATA(self, server, session, envelope):
        print('Receiving message from:', envelope.mail_from)
        print('Message for:', envelope.rcpt_tos)
        print('Message data:')
        for line in envelope.content.decode('utf8', errors='replace').splitlines():
            print(f'> {line.rstrip()}')
        print('End of message')
        return '250 Message accepted for delivery'

if __name__ == '__main__':
    handler = Handler()
    controller = Controller(handler, hostname='127.0.0.1', port=1025)
    controller.start()
    print(f'SMTP server running on 127.0.0.1:1025')
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass