# Copyright (c) 2010 Mark Sandstrom
# Copyright (c) 2011 Raphaël Barrois
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

class OrderedDeclaration(object):
    """A factory declaration.

    Ordered declarations keep track of the order in which they're defined so that later declarations
    can refer to attributes created by earlier declarations when the declarations are evaluated."""
    def evaluate(self, sequence, obj):
        """Evaluate this declaration.

        Args:
            factory: The factory this declaration was defined in.
            obj: The object holding currently computed attributes
            attributes: The attributes created by the unordered and ordered declarations up to this point."""

        raise NotImplementedError('This is an abstract method')


class LazyAttribute(OrderedDeclaration):
    def __init__(self, function):
        super(LazyAttribute, self).__init__()
        self.function = function

    def evaluate(self, sequence, obj):
        return self.function(obj)


class SelfAttribute(OrderedDeclaration):
    def __init__(self, attribute_name):
        super(SelfAttribute, self).__init__()
        self.attribute_name = attribute_name

    def evaluate(self, sequence, obj):
        return getattr(obj, self.attribute_name)


class Sequence(OrderedDeclaration):
    def __init__(self, function, type=str):
        super(Sequence, self).__init__()
        self.function = function
        self.type = type

    def evaluate(self, sequence, obj):
        return self.function(self.type(sequence))


class LazyAttributeSequence(Sequence):
    def evaluate(self, sequence, obj):
        return self.function(obj, self.type(sequence))


class SubFactory(OrderedDeclaration):
    """Base class for attributes based upon a sub-factory.

    Attributes:
        defaults: DeclarationsHolder, the declarations from the wrapped factory
        factory: Factory, the wrapped factory
    """

    def __init__(self, factory, **kwargs):
        super(SubFactory, self).__init__()
        self.defaults = kwargs
        self.factory = factory

    def evaluate(self, create, extra):
        """Evaluate the current definition and fill its attributes.

        Uses attributes definition in the following order:
        - attributes defined in the wrapped factory class
        - values defined when defining the SubFactory
        - additional values defined in attributes
        """

        defaults = dict(self.defaults)
        if extra:
            defaults.update(extra)

        attrs = self.factory.attributes(create, defaults)

        if create:
            return self.factory.create(**attrs)
        else:
            return self.factory.build(**attrs)

# Decorators... in case lambdas don't cut it

def lazy_attribute(func):
    return LazyAttribute(func)

def sequence(func):
    return Sequence(func)

def lazy_attribute_sequence(func):
    return LazyAttributeSequence(func)
