#function for format an image file
def upload_to(instance, filename):
	return 'tutoring/{filename}'.format(filename=filename)

#funtion for sorting by a dictionary attribute
def auxSort(dict):
	return dict['result']