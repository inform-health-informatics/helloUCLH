# Demonstration of EMAP platform
# - [ ] @TODO: (2019-02-01) play with ASCII art!
import time

the_boss = 'Niall'

intro = """

EMAP has been built

    ... here at UCLH

    ... for the NHS

according to the following principles ...

"""

emap_principles = """
1. Protection of operational systems
2. Protection of patient privacy:\n   A 'code to data' rather than 'data to code' paradigm
3. Near real-time over retrospective batch loads
4. Interoperability for semantic collaboration
5. Scalable through open source
"""

def type_text(s, pause):
    for c in list(s):
        time.sleep(pause)
        print(c, end='', flush=True)
    print('\n', end='', flush=True)


hello = '\nHello ' + the_boss + '\n'
type_text(hello, 0.02)

response = input('Shall I continue? ')
if response:
    text = intro + emap_principles
    for l in text.splitlines():
        time.sleep(0.3)
        type_text(l, 0.02)

time.sleep(1)
goodbye = '\nThank you and goodbye\n'
type_text(goodbye, 0.02)


