from lacore.source.chunked import ChunkedFile as BaseChunkedFile


class ChunkedFile(BaseChunkedFile):
    maxchunk = 20971520
