I am looking at the code and it’s really cool. Thanks for breaking everything down.
I am thinking that we should start simple, by making it beep.
Since there are 5 frequency bands that are being looked at, I am thinking we could eventually trigger 5 things?

Also, looking at the 	In[8] and In[10] functions I see that the data being written is the y=channel, and y=f_band, correct?
What is ‘ax’?

Since the read time is roughly 1 second, I am thinking that we can use the following scheme to trigger audio:
1. We store each individual band in individual variables.
2. Based on the input range, we scale/map those variables to audio frequency range (if we have 5 bands, perhaps 5 ranges).
3. We can then compare this value against the previous value, and if we see that the change/delta is greater than some value,
we tell the system to allow sound to come out. In analog synthesizers, a trigger is sent when a key is pressed telling the
amplifier to open. When the amplifier opens, it will allow the oscillators to sound in the output. We can hook it up in a
similar way.

I’ll start looking into this and we can see how the information can be passed when we meet.
Hopefully I’ll have something beeping by then.
