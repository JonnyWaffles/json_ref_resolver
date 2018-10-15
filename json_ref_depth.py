"""
Taken from a github `project <https://github.com/purukaushik/ref-resolver/blob/master/ref_resolver/ref_resolver.py>`_
and re-engineered to work.

This dumpster fire is a work in progress. I hate this code but I got it to work, so don't blame me. - Jonny
"""
from typing import Sequence, Tuple, Any, Union
from jsonschema import RefResolver


class ResolverDepth:
    """
    Recursively replaces Json schema references with the referenced content.

    Useful to see a full schema in one view.

    Attributes:
        item: The item to be resolved, usually a schema
        resolver: The resolver
        depth: Number of times the resolver should replace references with
            their content. If None all links will be resolved and the entire
            schema will be flattened.
    """

    def __init__(self, item: Any, resolver: RefResolver, depth: int=None):
        self.item = item
        self.resolver = resolver
        self.remaining_depth = depth

    def new_resolve(self, item: Any, remaining_depth: int) -> Any:
        """Returns the result of a new resolver.

        Args:
            item: Item to be resolved
            remaining_depth: How many links should be resolved
        """
        return ResolverDepth(item, self.resolver, remaining_depth).resolve()

    @property
    def follow_ref(self) -> bool:
        """Should the resolver continue or return the reference."""
        if self.remaining_depth is None:
            return True
        return self.remaining_depth > 0

    def resolve_ref(self, url: str) -> Tuple[str, Any]:
        """Resolve a $ref"""
        resolver = self.resolver

        resolver.push_scope(url)
        try:
            return resolver.resolve(url)
        finally:
            resolver.pop_scope()

    def resolve(self) -> Any:
        """Resolves this instance."""
        item = self.item
        url = self._is_reference(item)
        if url and not self.follow_ref:
            return item

        if isinstance(item, Sequence):
            return self.resolve_sequence()

        if isinstance(item, dict):
            return self.resolve_dict()

        return item

    def resolve_dict(self) -> dict:
        document = self.item
        ret = {}

        for key, value in document.items():
            url = self._is_reference(value)
            if url and self.follow_ref:
                _, item = self.resolve_ref(url)
                value = self.new_resolve(item, self.remaining_depth - 1)

            else:
                if isinstance(value, dict):
                    value = self.new_resolve(value, self.remaining_depth)

            ret.update({key: value})

        return ret

    def resolve_sequence(self) -> Sequence:
        sequence = self.item
        for index, item in enumerate(sequence):
            url = self._is_reference(item)
            if url and self.follow_ref:
                _, item = self.resolve_ref(url)
                sequence[index] = self.new_resolve(item, self.remaining_depth - 1)

            if isinstance(item, Sequence):
                sequence[index] = self.new_resolve(item, self.remaining_depth)

            if isinstance(item, dict):
                sequence[index] = self.new_resolve(item, self.remaining_depth)
        return sequence

    @staticmethod
    def _is_reference(item) -> Union[str, bool]:
        if isinstance(item, dict):
            return item.get('$ref', False)
        return False
