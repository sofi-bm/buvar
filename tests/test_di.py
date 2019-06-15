import pytest


@pytest.fixture
def event_loop(event_loop):
    from buvar import context, components

    cmps = components.Components()
    context.set_task_factory(cmps, loop=event_loop)
    return event_loop


@pytest.mark.asyncio
async def test_di(benchmark):
    from buvar import context, di

    class Foo(dict):
        def __init__(self, name=None):
            super().__init__(name=name, foo=True)

    @di.register
    class Bar(dict):
        def __init__(self, bar: Foo):
            super().__init__(foo=bar, bar=True)

    class Baz(dict):
        def __init__(self, **kwargs):
            super().__init__(baz=True, **kwargs)

    class Bim:
        pass

    @di.register
    def baz_adapter(
        bar: Bar,
        bam: Foo = 1,
        bim: Bim = 'default',
        *,
        foo: Foo = None
    ) -> Baz:
        return Baz(foo=foo, bam=bam, bim=bim, bar=bar)

    context.add(Foo())
    context.add(Foo(name='bar'), name='bar')

    baz, = benchmark(di.nject, Baz)
    assert isinstance(baz, Baz)
    assert baz == {
        'baz': True,
        'bam': {'foo': True, 'name': None},
        'foo': {'foo': True, 'name': None},
        'bim': 'default',
        'bar': {'bar': True, 'foo': {'foo': True, 'name':  'bar'}},
    }
