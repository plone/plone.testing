"""Zope2-specific helpers and layers
"""

def installProduct(productName, quiet=True):
    """Install the Zope 2 product with the given name, so that it will show
    up in the Zope 2 control panel and have its ``initialize()`` hook called.
    
    If ``quiet`` is False, an error will be logged if the product cannot be
    found. By default, the function is silent.
    """
    
    raise NotImplementedError()
