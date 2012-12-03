sitemap = {}

def add_to_sitemap(priority = '0'):
	def decorator(func):
		sitemap['.'.join(func.__name__.replace('index', '/').rsplit('_', 1))] = priority
		return func
	return decorator