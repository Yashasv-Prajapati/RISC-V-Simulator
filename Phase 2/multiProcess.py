import multiprocessing as mp
import time
from multiprocessing import Manager


def fetch(counter):
    time.sleep(2)
    print("Fetch", counter[0])
    counter[0] += 1
def decode(counter):
    time.sleep(1.5)
    print("Decode", counter[1])
    counter[1] += 1
    
def execute(counter):
    time.sleep(1)
    print("Execute", counter[2])
    counter[2] = counter[2] + 1
    
def Memory(counter):
    time.sleep(0.8)
    print("Memory", counter[3])
    counter[3] += 1
    
def Write(counter):
    time.sleep(0.01)
    print("Write", counter[4])
    counter[4] += 1
    
    
if __name__ == "__main__":
    
    with Manager() as manager:

        process_list = []

        # for i in range(10):
        #     p =  mp.Process(target= fetch(counter))
        #     p.start()
        #     process_list.append(p)
        # p1 =  mp.Process(target= fetch, args=[counter])

        l = manager.list([0]*5)
                
        for i in range(3):
            p1 =  mp.Process(target= fetch, args=[l])
            p2 =  mp.Process(target= decode, args=[l])
            p3 =  mp.Process(target= execute, args=[l])
            p4 =  mp.Process(target= Memory, args=[l])
            p5 =  mp.Process(target= Write, args=[l])
            
            p1.start()
            p2.start()
            p3.start()
            p4.start()
            p5.start()

            process_list.append(p1)
            process_list.append(p2)
            process_list.append(p3)
            process_list.append(p4)
            process_list.append(p5)

            for process in process_list:
                process.join()
            print("---------------")


