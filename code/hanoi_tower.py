def move(nb_disk, origin, target, tmp):
	if nb_disk >= 1:
		move(nb_disk - 1, origin, tmp, target)
		print 'move disk from {} to {}'.format(origin, target)
		move(nb_disk - 1, tmp, target, origin)

move(3, 1, 3, 2)
