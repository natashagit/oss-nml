from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.generate_request_response_schema_type_0 import GenerateRequestResponseSchemaType0


T = TypeVar("T", bound="GenerateRequest")


@_attrs_define
class GenerateRequest:
    """Request payload for generate endpoint.

    Attributes:
        user_input (str): The text provided by the chat user.
        system_prompt (str): Instructional system prompt.
        response_schema (GenerateRequestResponseSchemaType0 | None | Unset): Optional JSON schema dict for structured
            responses.
    """

    user_input: str
    system_prompt: str
    response_schema: GenerateRequestResponseSchemaType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.generate_request_response_schema_type_0 import GenerateRequestResponseSchemaType0

        user_input = self.user_input

        system_prompt = self.system_prompt

        response_schema: dict[str, Any] | None | Unset
        if isinstance(self.response_schema, Unset):
            response_schema = UNSET
        elif isinstance(self.response_schema, GenerateRequestResponseSchemaType0):
            response_schema = self.response_schema.to_dict()
        else:
            response_schema = self.response_schema

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_input": user_input,
                "system_prompt": system_prompt,
            }
        )
        if response_schema is not UNSET:
            field_dict["response_schema"] = response_schema

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.generate_request_response_schema_type_0 import GenerateRequestResponseSchemaType0

        d = dict(src_dict)
        user_input = d.pop("user_input")

        system_prompt = d.pop("system_prompt")

        def _parse_response_schema(data: object) -> GenerateRequestResponseSchemaType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                response_schema_type_0 = GenerateRequestResponseSchemaType0.from_dict(data)

                return response_schema_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GenerateRequestResponseSchemaType0 | None | Unset, data)

        response_schema = _parse_response_schema(d.pop("response_schema", UNSET))

        generate_request = cls(
            user_input=user_input,
            system_prompt=system_prompt,
            response_schema=response_schema,
        )

        generate_request.additional_properties = d
        return generate_request

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
