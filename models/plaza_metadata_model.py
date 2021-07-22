from dataclasses import dataclass
from typing import Any, TypeVar, Type, cast


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class Song:
    id: str
    artist: str
    title: str
    album: str
    position: int
    length: int
    artwork_src: str
    artwork_sm_src: str
    reactions: int

    @staticmethod
    def from_dict(obj: Any) -> 'Song':
        assert isinstance(obj, dict)
        id = from_str(obj.get("id"))
        artist = from_str(obj.get("artist"))
        title = from_str(obj.get("title"))
        album = from_str(obj.get("album"))
        position = from_int(obj.get("position"))
        length = from_int(obj.get("length"))
        artwork_src = from_str(obj.get("artwork_src"))
        artwork_sm_src = from_str(obj.get("artwork_sm_src"))
        reactions = from_int(obj.get("reactions"))
        return Song(id, artist, title, album, position, length, artwork_src, artwork_sm_src, reactions)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_str(self.id)
        result["artist"] = from_str(self.artist)
        result["title"] = from_str(self.title)
        result["album"] = from_str(self.album)
        result["position"] = from_int(self.position)
        result["length"] = from_int(self.length)
        result["artwork_src"] = from_str(self.artwork_src)
        result["artwork_sm_src"] = from_str(self.artwork_sm_src)
        result["reactions"] = from_int(self.reactions)
        return result


@dataclass
class PlazaMetadata:
    song: Song
    listeners: int
    updated_at: int

    @staticmethod
    def from_dict(obj: Any) -> 'PlazaMetadata':
        assert isinstance(obj, dict)
        song = Song.from_dict(obj.get("song"))
        listeners = from_int(obj.get("listeners"))
        updated_at = from_int(obj.get("updated_at"))
        return PlazaMetadata(song, listeners, updated_at)

    def to_dict(self) -> dict:
        result: dict = {}
        result["song"] = to_class(Song, self.song)
        result["listeners"] = from_int(self.listeners)
        result["updated_at"] = from_int(self.updated_at)
        return result


def plaza_metadata_from_dict(s: Any) -> PlazaMetadata:
    return PlazaMetadata.from_dict(s)


def plaza_metadata_to_dict(x: PlazaMetadata) -> Any:
    return to_class(PlazaMetadata, x)
