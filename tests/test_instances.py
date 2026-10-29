from quantumbench.instances import create_default_suite, create_instance


def test_default_suite_has_unique_identifiers():
    suite = create_default_suite()
    identifiers = [instance.instance_id for instance in suite]

    assert len(suite) == 5
    assert len(identifiers) == len(set(identifiers))


def test_instance_generation_is_reproducible():
    first = create_instance(6, 0.5, 42)
    second = create_instance(6, 0.5, 42)

    assert first.instance_id == second.instance_id
    assert list(first.graph.edges(data=True)) == list(
        second.graph.edges(data=True)
    )