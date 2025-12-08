from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.generate_response_result_type_1 import GenerateResponseResultType1


T = TypeVar("T", bound="GenerateResponse")


@_attrs_define
class GenerateResponse:
    """Response payload for generate endpoint.

    Attributes:
        result (GenerateResponseResultType1 | str): String response or structured dict.
    """

    result: GenerateResponseResultType1 | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.generate_response_result_type_1 import GenerateResponseResultType1

        result: dict[str, Any] | str
        if isinstance(self.result, GenerateResponseResultType1):
            result = self.result.to_dict()
        else:
            result = self.result

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "result": result,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.generate_response_result_type_1 import GenerateResponseResultType1

        d = dict(src_dict)

        def _parse_result(data: object) -> GenerateResponseResultType1 | str:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                result_type_1 = GenerateResponseResultType1.from_dict(data)

                return result_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GenerateResponseResultType1 | str, data)

        result = _parse_result(d.pop("result"))

        generate_response = cls(
            result=result,
        )

        generate_response.additional_properties = d
        return generate_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
