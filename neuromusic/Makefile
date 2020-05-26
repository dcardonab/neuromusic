# connect muse headset using address
# address found by turning Muse on and running in a terminal `sudo hcitool lescan`
ADDRESS= "00:55:DA:B7:74:0D"

connect:
	@python muse-lsl.py --address ${ADDRESS}

reqs:
	@$(shell conda list -e > requirements.txt)