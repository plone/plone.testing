
_marker = object()

class ResourceManager(object):
    """Mixin class for 
    """
    
    __bases__ = ()
    
    def __init__(self):
        self._resources = {}
    
    def __getitem__(self, key):
        item = self.get(key, _marker)
        if item is _marker:
            raise KeyError(key)
        return item
    
    def get(self, key, default=None):
        for resourceManager in self.resourceResolutionOrder():
            if key in resourceManager._resources:
                return resourceManager._resources[key]
        return default
    
    def __setitem__(self, key, value):
        self._resources[key] = value
    
    def __delitem__(self, key):
        del self._resources[key]
    
    def resourceResolutionOrder(self):
        """Get the order in which resources are resolved
        """
        
        return tuple(self._mro(self))
    
    # This is basically the Python MRO algorithm, adapted from
    # http://www.python.org/download/releases/2.3/mro/
    
    def _merge(self, seqs):
        
        res = []
        i = 0
        
        while True:
            nonemptyseqs = [seq for seq in seqs if seq]
          
            if not nonemptyseqs:
                return res
          
            i += 1
          
            for seq in nonemptyseqs: # find merge candidates among seq heads
                cand = seq[0]
                nothead=[s for s in nonemptyseqs if cand in s[1:]]
                if nothead:
                    cand=None #reject candidate
                else:
                    break
          
            if not cand:
                raise ValueError(u"Inconsistent layer hierarchy!")
            
            res.append(cand)
            for seq in nonemptyseqs: # remove cand
                if seq[0] == cand:
                    del seq[0]
    
    def _mro(self, instance):
        return self._merge(
                [ [instance] ] + 
                map(self._mro, instance.__bases__) + 
                [ list(instance.__bases__) ]
            )
    
class Layer(ResourceManager):
    """A base class for layers.
    """
    
    # Set this at the class level to a tuple of layer *instances* to treat
    # as bases for this layer. This may be overridden by passing a tuple
    # to the Layer constructor.

    __bases__ = ()
    
    def __init__(self, bases=None, name=None, module=None):
        """Create an instance of the layer. Normally this is done once, at
        module scope.
        
        Pass a tuple of bases to override the default set of bases.
        
        Pass a name to override the layer name. By default, it is the
        name of the layer class.
        
        Pass a module to override the layer module. By default, it is the
        module of the layer class.
        """
        super(Layer, self).__init__()
        
        if bases is not None:
            self.__bases__ = tuple(bases)
        
        if name is None:
            name = self.__class__.__name__
        self.__name__ = name
        
        if module is None:
            module = self.__class__.__module__
        self.__module__ = module
    
    def __repr__(self):
        return "<Layer '%s.%s'>" % (self.__module__, self.__name__,)
    
    # Layer lifecycle methods - overriden by subclasses
        
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def setUpTest(self):
        pass
    
    def tearDownTest(self):
        pass

def layered(suite, layer):
    """Add the given layer to each suite in the list of suites passed
    """
    
    suite.layer = layer
    return suite
