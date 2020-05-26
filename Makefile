# connect muse headset using address
ADDRESS= "00:55:DA:B7:74:0D"

connect:
	@python muse-lsl.py --address ${ADDRESS}
