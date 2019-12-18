from sys import argv

def main():
	if not len(argv) == 2:
		raise Exception("Please provide file as argument")
	file = open(argv[1], 'r')
	output = file.read()
	jmps = output.split("\n\n")

	nope_jumps = []
	for jmp in jmps:
		words = jmp.rstrip().split()
		if len(words) > 10 and words[5] == 'nop' and words[8] == 'nop' and words[11] == 'nop' and words[14] == 'jmp':
			nope_jumps.append(words[12]+' '+words[13]+' '+words[14]+' '+words[15])
	print_(nope_jumps)

def print_(nope_jumps):
	for jmp in nope_jumps:
		print(jmp)

		
if __name__ == "__main__":
    main()