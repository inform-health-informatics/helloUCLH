# Demonstration of EMAP platform
# - [ ] @TODO: (2019-02-01) play with ASCII art!
import time

the_boss = 'Niall'
emap_principles = """
1. Protection of operational systems
2. Protection of patient privacy:    A 'code to data' rather than 'data to code' paradigm
3. Near real-time over retrospective batch loads
4. Interoperability for semantic collaboration
5. Scalable through open source
"""

print('Hello', the_boss)
response = input('Shall I continue? ')
if response:
    text = '\nEMAP has been built for the NHS at UCLH according to the following principles ...\n'
    text = text + emap_principles
    for l in text.splitlines():
        time.sleep(0.3)
        for c in list(l):
            time.sleep(0.02)
            print(c, end='', flush=True)
        print('\n', flush=True)


time.sleep(1)
print('Thank you and goodbye')

