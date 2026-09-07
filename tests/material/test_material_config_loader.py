from pathlib import Path

from src.material.config_loader import MaterialConfigLoader

MATERIALS_CONFIG_PATH = Path("./config/materials/materials_registry.yaml")


def test_load_all_material_templates():
    loader = MaterialConfigLoader(MATERIALS_CONFIG_PATH)

    templates = loader.load_all()

    assert isinstance(templates, dict)

    assert "concrete" in templates
    assert "reinforcing_steel" in templates
    assert "reinforcement_mesh" in templates
    assert "reinforcement_accessory" in templates


def test_load_concrete_template():
    loader = MaterialConfigLoader(MATERIALS_CONFIG_PATH)

    templates = loader.load_all()
    concrete = templates["concrete"]

    assert concrete.material_type == "concrete"

    keyword_values = {keyword.value for keyword in concrete.keywords}

    assert "Beton" in keyword_values
    assert "Normalbeton" in keyword_values

    assert "strength_class" in concrete.core_attributes
    assert "exposure_class" in concrete.core_attributes
    assert "moisture_class" in concrete.core_attributes
    assert "consistency_class" in concrete.core_attributes
    assert "max_aggregate_size" in concrete.core_attributes


def test_load_concrete_strength_class():
    loader = MaterialConfigLoader(MATERIALS_CONFIG_PATH)

    templates = loader.load_all()
    concrete = templates["concrete"]

    strength_class = concrete.core_attributes["strength_class"]

    assert strength_class.name == "strength_class"
    assert strength_class.value_type == "single"

    assert "C25/30" in strength_class.values
    assert "C30/37" in strength_class.values
    assert "C35/45" in strength_class.values


def test_load_numeric_attribute():
    loader = MaterialConfigLoader(MATERIALS_CONFIG_PATH)

    templates = loader.load_all()
    concrete = templates["concrete"]

    max_aggregate_size = concrete.core_attributes["max_aggregate_size"]

    assert max_aggregate_size.name == "max_aggregate_size"
    assert max_aggregate_size.value_type == "numeric"
    assert max_aggregate_size.unit == "mm"


def test_load_supplementary_attribute():
    loader = MaterialConfigLoader(MATERIALS_CONFIG_PATH)

    templates = loader.load_all()
    concrete = templates["concrete"]

    concrete_type = concrete.supplementary_attributes["concrete_type"]

    assert concrete_type.name == "concrete_type"
    assert concrete_type.value_type == "single"

    assert "Normalbeton" in concrete_type.values
    assert "Leichtbeton" in concrete_type.values
    assert "Schwerbeton" in concrete_type.values


def test_print_all_material_templates():
    loader = MaterialConfigLoader(MATERIALS_CONFIG_PATH)

    templates = loader.load_all()

    for material_type, template in templates.items():
        print("\n" + "=" * 80)
        print(f"Material: {material_type}")
        print("=" * 80)

        print("\nKeywords:")
        for keyword in template.keywords:
            print(f"  - {keyword.value} [{keyword.level.value}]")

        print("\nCore attributes:")
        for name, attribute in template.core_attributes.items():
            print(f"  {name}")
            print(f"    type: {attribute.value_type}")

            if attribute.unit is not None:
                print(f"    unit: {attribute.unit}")

            if attribute.values:
                print("    values:")
                for value in attribute.values:
                    print(f"      - {value}")

            if attribute.groups:
                print("    groups:")

                for group_name, group_data in attribute.groups.items():
                    print(f"      {group_name}")

                    values = group_data.get("values", [])

                    for value in values:
                        print(f"        - {value}")

        print("\nSupplementary attributes:")
        for name, attribute in template.supplementary_attributes.items():
            print(f"  {name}")
            print(f"    type: {attribute.value_type}")

            if attribute.unit is not None:
                print(f"    unit: {attribute.unit}")

            if attribute.values:
                print("    values:")
                for value in attribute.values:
                    print(f"      - {value}")

            if attribute.groups:
                print("    groups:")

                for group_name, group_data in attribute.groups.items():
                    print(f"      {group_name}")

                    values = group_data.get("values", [])

                    for value in values:
                        print(f"        - {value}")


def test_load_concrete_keyword_levels():
    loader = MaterialConfigLoader(MATERIALS_CONFIG_PATH)

    templates = loader.load_all()
    concrete = templates["concrete"]

    keywords = {keyword.value: keyword.level.value for keyword in concrete.keywords}

    assert keywords["Normalbeton"] == "high"
    assert keywords["Beton"] == "low"
