import xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path

from src.ingestion.gaeb_lv_loader import GAEBLVLoader
from src.models import LVPosition

GAEB_NAMESPACE = "http://www.gaeb.de/GAEB_DA_XML/200407"


def create_element(xml: str) -> ET.Element:
    return ET.fromstring(xml)


def test_get_namespace():
    root = create_element(
        f"""
        <GAEB xmlns="{GAEB_NAMESPACE}">
        </GAEB>
        """
    )

    namespace = GAEBLVLoader._get_namespace(root)

    assert namespace == {"gaeb": GAEB_NAMESPACE}


def test_get_namespace_without_namespace():
    root = create_element(
        """
        <GAEB>
        </GAEB>
        """
    )

    namespace = GAEBLVLoader._get_namespace(root)

    assert namespace == {}


def test_build_oz():
    oz = GAEBLVLoader._build_oz(
        category_parts=["2", "7"],
        category_lengths=[2, 2],
        item_r_no_part="170",
        item_length=4,
    )

    assert oz == "02.07.0170"


def test_build_oz_with_small_item_number():
    oz = GAEBLVLoader._build_oz(
        category_parts=["2", "5"],
        category_lengths=[2, 2],
        item_r_no_part="10",
        item_length=4,
    )

    assert oz == "02.05.0010"


def test_clean_text():
    element = create_element(
        """
        <DetailTxt>
            <Text>
                <p>
                    <span>Rahmendecke aus Stahlbeton,</span>
                    <br/>
                    <span>DIN EN 206</span>
                </p>
            </Text>
        </DetailTxt>
        """
    )

    text = GAEBLVLoader._clean_text(element)

    assert text == ("Rahmendecke aus Stahlbeton, DIN EN 206")


def test_clean_text_removes_gaeb_markers():
    element = create_element(
        """
        <DetailTxt>
            <Text>
                <span>Bauteil:</span>
            </Text>
            <TextComplement>
                <ComplBody>
                    <span>'(&gt;für den Höhensprung mit Auskragung&lt;) '</span>
                </ComplBody>
            </TextComplement>
        </DetailTxt>
        """
    )

    text = GAEBLVLoader._clean_text(
        element,
        clean_gaeb_markers=True,
    )

    assert text == ("Bauteil: für den Höhensprung mit Auskragung")


def test_clean_text_returns_empty_string_for_none():
    text = GAEBLVLoader._clean_text(None)

    assert text == ""


def test_read_oz_structure():
    boq_info = create_element(
        f"""
        <BoQInfo xmlns="{GAEB_NAMESPACE}">
            <BoQBkdn>
                <Type>BoQLevel</Type>
                <Length>2</Length>
            </BoQBkdn>

            <BoQBkdn>
                <Type>BoQLevel</Type>
                <Length>2</Length>
            </BoQBkdn>

            <BoQBkdn>
                <Type>Item</Type>
                <Length>4</Length>
            </BoQBkdn>

            <BoQBkdn>
                <Type>Index</Type>
                <Length>1</Length>
            </BoQBkdn>
        </BoQInfo>
        """
    )

    namespace = {"gaeb": GAEB_NAMESPACE}

    category_lengths, item_length = GAEBLVLoader._read_oz_structure(
        boq_info=boq_info,
        namespace=namespace,
    )

    assert category_lengths == [2, 2]
    assert item_length == 4


def test_read_item():
    item = create_element(
        f"""
        <Item
            xmlns="{GAEB_NAMESPACE}"
            ID="AAAAAAABIEPJCEOI"
            RNoPart="170"
        >
            <Qty>1.000</Qty>
            <QU>psch</QU>

            <Description>
                <CompleteText>

                    <DetailTxt>
                        <Text>
                            <p>
                                <span>
                                    Bewehrungsanschlüsse
                                    mit Schraubverbindungen
                                </span>
                            </p>
                        </Text>

                        <TextComplement>
                            <ComplCaption>
                                <span>Bauteil:</span>
                            </ComplCaption>

                            <ComplBody>
                                <span>
                                    '(&gt;für den Höhensprung&lt;) '
                                </span>
                            </ComplBody>
                        </TextComplement>
                    </DetailTxt>

                    <OutlineText>
                        <OutlTxt>
                            <TextOutlTxt>
                                <p>
                                    <span>
                                        Schraub-Bewehrungsanschlüsse
                                    </span>
                                </p>
                            </TextOutlTxt>
                        </OutlTxt>
                    </OutlineText>

                </CompleteText>
            </Description>
        </Item>
        """
    )

    namespace = {"gaeb": GAEB_NAMESPACE}

    position = GAEBLVLoader._read_item(
        item=item,
        category_parts=["2", "7"],
        category_lengths=[2, 2],
        item_length=4,
        namespace=namespace,
    )

    assert isinstance(position, LVPosition)

    assert position.gaeb_id == "AAAAAAABIEPJCEOI"
    assert position.oz == "02.07.0170"
    assert position.quantity == Decimal("1.000")
    assert position.unit == "psch"

    assert position.short_text == ("Schraub-Bewehrungsanschlüsse")

    assert position.long_text == (
        "Bewehrungsanschlüsse mit Schraubverbindungen Bauteil: für den Höhensprung"
    )


def test_load_reads_positions(
    tmp_path: Path,
    monkeypatch,
):
    xml_file = tmp_path / "test.X83"

    xml_file.write_text(
        f"""
        <?xml version="1.0" encoding="UTF-8"?>

        <GAEB xmlns="{GAEB_NAMESPACE}">

            <PrjInfo>
                <NamePrj>Test Project</NamePrj>
                <LblPrj>Test LV</LblPrj>
            </PrjInfo>

            <Award>

                <BoQ>

                    <BoQInfo>

                        <BoQBkdn>
                            <Type>BoQLevel</Type>
                            <Length>2</Length>
                        </BoQBkdn>

                        <BoQBkdn>
                            <Type>BoQLevel</Type>
                            <Length>2</Length>
                        </BoQBkdn>

                        <BoQBkdn>
                            <Type>Item</Type>
                            <Length>4</Length>
                        </BoQBkdn>

                    </BoQInfo>

                    <BoQBody>

                        <BoQCtgy RNoPart="2">

                            <BoQBody>

                                <BoQCtgy RNoPart="7">

                                    <BoQBody>

                                        <Itemlist>

                                            <Item
                                                ID="TEST-ID"
                                                RNoPart="170"
                                            >
                                                <Qty>1.000</Qty>
                                                <QU>psch</QU>

                                                <Description>
                                                    <CompleteText>

                                                        <DetailTxt>
                                                            <Text>
                                                                <p>
                                                                    <span>
                                                                        Test Longtext
                                                                    </span>
                                                                </p>
                                                            </Text>
                                                        </DetailTxt>

                                                        <OutlineText>
                                                            <OutlTxt>
                                                                <TextOutlTxt>
                                                                    <p>
                                                                        <span>
                                                                            Test Kurztext
                                                                        </span>
                                                                    </p>
                                                                </TextOutlTxt>
                                                            </OutlTxt>
                                                        </OutlineText>

                                                    </CompleteText>
                                                </Description>

                                            </Item>

                                        </Itemlist>

                                    </BoQBody>

                                </BoQCtgy>

                            </BoQBody>

                        </BoQCtgy>

                    </BoQBody>

                </BoQ>

            </Award>

        </GAEB>
        """.strip(),
        encoding="utf-8",
    )

    monkeypatch.setenv(
        "LV_FILE_PATH",
        str(xml_file),
    )

    positions = GAEBLVLoader.load()

    assert len(positions) == 1

    position = positions[0]

    assert position.gaeb_id == "TEST-ID"
    assert position.oz == "02.07.0170"
    assert position.quantity == Decimal("1.000")
    assert position.unit == "psch"
    assert position.short_text == "Test Kurztext"
    assert position.long_text == "Test Longtext"
