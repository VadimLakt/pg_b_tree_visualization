import resource
import os
import re
import sys

class Block:

    def __init__(self):
        self.dataItems = []

fillcolor = ["aquamarine1", "lightblue", "lightcoral"]

file_name = None
if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_name = sys.argv[1]

if file_name == None:
    raise Exception("File not specified")


print(f'File Size is {os.stat(file_name).st_size / (1024 * 1024)} MB')

txt_file = open(file_name)

count = 0
countBlock = 0
countDeadBlock = 0

blockNumber = None
isSpecialSection = False
isDataSection = False
isDeletedBlock = False

nodes = [[]]

for line in txt_file:
    # We can process file line by line here, for simplicity I am taking count of lines
    count += 1
    if re.match("^Block", line):
        # remember previous block if alive
        if not isDeletedBlock and blockNumber is not None:
            if levelBlock is None:
                raise Exception("Level of Block " + blockNumber + " is None")

            if blockNumber != '0':
                while int(levelBlock) >= len(nodes):
                    nodes.append([])
                if levelBlock == '0':
                    block.dataItems = []
                nodes[int(levelBlock)].append(block)

        block = Block()

        isSpecialSection = False
        isDataSection = False
        levelBlock = None

        countBlock += 1

        blockNumber = line.replace("Block ", "").replace("*", "").replace(" ", "").replace("\n", "")
        block.blockNumber = blockNumber
    elif re.match("<Special Section> -----", line):
       isDataSection = False

       isSpecialSection = True 
    elif re.match("<Data> -----", line):
        isSpecialSection = False

        isDataSection = True
    else:
        if isSpecialSection:
            if re.match("  Flags: ", line):
                isDeletedBlock = "DELETED" in line
                if isDeletedBlock:
                    countDeadBlock += 1

            if re.match("  Blocks: ", line):
                privBlFind = re.search('Previous \((.+?)\) ', line)
                if privBlFind:
                    block.previousBlock = privBlFind.group(1)
                
                nextBlFind = re.search('Next \((.+?)\) ', line)
                if nextBlFind:
                    block.nextBlock = nextBlFind.group(1)

                levelBlFind = re.search('Level \((.+?)\) ', line)
                if levelBlFind:
                    levelBlock = levelBlFind.group(1)
                    block.levelBlock = levelBlFind.group(1)
        elif isDataSection:
            if re.match("  Block Id:", line):
                dataItemsFind = re.search('  Block Id: (.+?) ', line)
                if dataItemsFind:
                    dat = dataItemsFind.group(1)
                    if dat != '0':
                        block.dataItems.append(dataItemsFind.group(1))

# Last block
if not isDeletedBlock and blockNumber is not None:
    if levelBlock is None:
        raise Exception("Level of Block " + blockNumber + " is None")
    if blockNumber != '0':
        while int(levelBlock) >= len(nodes):
            nodes.append([])
        if levelBlock == '0':
            block.dataItems = []
        nodes[int(levelBlock)].append(block)

txt_file.close()

# Get result
f = open("result.dot", "w")
f.write("digraph \"tree test\" {" + "\n" +
        "  splines=true" + "\n" +
        "  ranksep=15" + "\n" +
        "  rankdir=LR" + "\n" +
        "  node [shape=rect style=\"rounded,filled\"]" + "\n" +
        "  {rank=same" + "\n")

for cntNode, node in enumerate(nodes):
    for block in node:
        f.write(
        "    " + block.blockNumber + " [label=<" + "\n" +
        "      <table border=\"0\" cellspacing=\"0\" cellborder=\"1\">" + "\n" +
        "      <tr><td> " + block.blockNumber + "</td></tr>" + "\n"
        )
        for cntItem, items in enumerate(block.dataItems):
            f.write(
            "      <tr><td port=\"" + items + "\" style=\"rounded\" bgcolor=\"lightcyan\">" + str(cntItem) + "</td></tr>" + "\n"
            )

        f.write(
            "      </table>>" + "\n" +
            "      fillcolor=" + fillcolor[cntNode % len(fillcolor)] + "\n" +
            "    ]" + "\n"
        )
    f.write("  }" + "\n")
    for block in node:
        if block.previousBlock != '0':
            f.write(block.blockNumber + "->" + block.previousBlock + "[color=red]\n")
        if block.nextBlock != '0':
            f.write(block.blockNumber + "->" + block.nextBlock + "[color=green]\n")
        if cntNode != 0:
            for items in block.dataItems:
                if items != '0':
                    f.write(
                        block.blockNumber  + ":" + items + "->" + items + "\n"
                    )

    if cntNode + 1 != len(nodes):
        f.write("    {rank=same" + "\n")

f.write("}")

print(f'Number of Lines in the file is {count}')
print(f'Number of Block in the file is {countBlock}')
print(f'Number of Dead Block in the file is {countDeadBlock}')

print('Peak Memory Usage =', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
print('User Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_utime)
print('System Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_stime)