from ctxwriter import ContextThreadWriter


class ListWriter(ContextThreadWriter):

    def __init__(self, out: list, lim: int = 5):
        super().__init__(lim)
        self.out = out 

    def write(self, dat):
        self.out += dat

if __name__ == '__main__':

    result = []
    sample = [
        ['Just a couple of sentences', 'Nothing to worry about'],
        ['I like sentences, too', 'Here, lets see what happens', 'If I add another sentence.'],
        ['And finally one or two more', 'Sentences to see what happens.']
    ]
    
    with ListWriter(result, lim=3) as lw:
        for s in sample:
            lw + s
    print(result)

    # ['Just a couple of sentences', 'Nothing to worry about', 'I like sentences, too', 
    # 'Here, lets see what happens', 'If I add another sentence.', 'And finally one or two more', 
    # 'Sentences to see what happens.']
