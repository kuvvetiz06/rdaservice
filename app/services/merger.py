from app.domain.models import FieldResult


class ResultMerger:
    @staticmethod
    def merge_fields(
        regex_fields: dict[str, FieldResult],
        llm_fields: dict[str, FieldResult],
    ) -> dict[str, FieldResult]:
        merged: dict[str, FieldResult] = {}
        all_fields = set(regex_fields.keys()) | set(llm_fields.keys())

        for field_name in all_fields:
            regex_field = regex_fields.get(field_name)
            llm_field = llm_fields.get(field_name)

            if (
                regex_field
                and regex_field.value not in (None, "")
                and regex_field.confidence >= 0.9
            ):
                merged[field_name] = regex_field
            elif llm_field and llm_field.value not in (None, ""):
                merged[field_name] = llm_field

        return merged
