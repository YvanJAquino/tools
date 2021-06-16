from ctxwriter import ContextThreadWriter
import time


class SleepyListWriter(ContextThreadWriter):

    def __init__(self, out: list, lim: int = 5):
        super().__init__(lim)
        self.out = out 

    def write(self, dat):
        self.out += dat
        time.sleep(1) # Added to prove continued execution
        

if __name__ == '__main__':

    result = []
    sample = [
        ['Just a couple of sentences', 'Nothing to worry about'],
        ['I like sentences, too', 'Here, lets see what happens', 'If I add another sentence.'],
        ['And finally one or two more', 'Sentences to see what happens.']
    ]

    with SleepyListWriter(result, lim=3) as slw:
        for s in sample:
            slw + s
            print("Yep, I've continued to execute..!")
    print(result)

    # ['Just a couple of sentences', 'Nothing to worry about', 'I like sentences, too', 
    # 'Here, lets see what happens', 'If I add another sentence.', 'And finally one or two more', 
    # 'Sentences to see what happens.']
