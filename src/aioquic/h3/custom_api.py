import logging
from typing import Dict, List, Optional, Tuple
from aioquic.buffer import encode_uint_var
from aioquic.h3.connection import (
    H3Connection, 
    FrameType, 
    StreamType, 
    encode_frame, 
    encode_settings,
    Headers
)
from aioquic.h3.events import H3Event
from aioquic.quic.connection import QuicConnection
from aioquic.quic.events import QuicEvent
import pylsqpack

logger = logging.getLogger("http3.custom_api")


class H3CustomAPI:
    """
    Custom HTTP/3 API for non-conformance testing.
    
    Provides atomic operations to manually control HTTP/3 frame sending
    and bypass normal protocol constraints for testing purposes.
    """
    
    def __init__(self, quic: QuicConnection, enable_webtransport: bool = False):
        """
        Initialize the custom H3 API.
        
        :param quic: A QuicConnection instance
        :param enable_webtransport: Whether to enable WebTransport
        """
        # Create H3Connection with settings frame skipped to have full manual control
        self._h3 = H3Connection(
            quic=quic, 
            enable_webtransport=enable_webtransport,
            skip_settings_frame=True
        )
        self._quic = quic
        
        # Track manually created streams
        self._manual_control_stream_id: Optional[int] = None
        self._manual_encoder_stream_id: Optional[int] = None
        self._manual_decoder_stream_id: Optional[int] = None
    
    def handle_event(self, event: QuicEvent) -> List[H3Event]:
        """
        Handle a QUIC event and return HTTP/3 events.
        
        :param event: The QUIC event to handle
        """
        return self._h3.handle_event(event)
    
    def create_control_stream(self) -> int:
        """
        Manually create a control stream without sending any frames.
        
        :return: The stream ID of the created control stream
        """
        stream_id = self._quic.get_next_available_stream_id(is_unidirectional=True)
        self._manual_control_stream_id = stream_id
        
        # Send stream type identifier
        self._quic.send_stream_data(stream_id, encode_uint_var(StreamType.CONTROL))
        
        return stream_id
    
    def create_encoder_stream(self) -> int:
        """
        Manually create a QPACK encoder stream.
        
        :return: The stream ID of the created encoder stream
        """
        stream_id = self._quic.get_next_available_stream_id(is_unidirectional=True)
        self._manual_encoder_stream_id = stream_id
        
        # Send stream type identifier
        self._quic.send_stream_data(stream_id, encode_uint_var(StreamType.QPACK_ENCODER))
        
        return stream_id
    
    def create_decoder_stream(self) -> int:
        """
        Manually create a QPACK decoder stream.
        
        :return: The stream ID of the created decoder stream
        """
        stream_id = self._quic.get_next_available_stream_id(is_unidirectional=True)
        self._manual_decoder_stream_id = stream_id
        
        # Send stream type identifier
        self._quic.send_stream_data(stream_id, encode_uint_var(StreamType.QPACK_DECODER))
        
        return stream_id
    
    def send_settings_frame(self, stream_id: int, settings: Optional[Dict[int, int]] = None) -> None:
        """
        Send a SETTINGS frame on the specified stream.
        
        :param stream_id: The stream ID to send the frame on
        :param settings: Optional custom settings dict, uses default if None
        """
        if settings is None:
            settings = self._h3._get_local_settings()
        
        frame_data = encode_settings(settings)
        encoded_frame = encode_frame(FrameType.SETTINGS, frame_data)
        
        self._quic.send_stream_data(stream_id, encoded_frame)
    
    def send_priority_update_frame(self, stream_id: int, prioritized_element_id: int, priority_field: bytes = b"") -> None:
        """
        Send a PRIORITY_UPDATE frame on the specified stream.
        
        :param stream_id: The stream ID to send the frame on
        :param prioritized_element_id: The ID of the element being prioritized
        :param priority_field: The priority field value
        """
        # PRIORITY_UPDATE frame format: prioritized_element_id + priority_field
        frame_data = encode_uint_var(prioritized_element_id) + priority_field
        encoded_frame = encode_frame(FrameType.PRIORITY_UPDATE, frame_data)
        
        self._quic.send_stream_data(stream_id, encoded_frame)
    
    def send_headers_frame(self, stream_id: int, headers: Headers, end_stream: bool = False) -> None:
        """
        Send a HEADERS frame on the specified stream.
        
        :param stream_id: The stream ID to send the frame on
        :param headers: The headers to send
        :param end_stream: Whether to end the stream
        """
        self._h3.send_headers(stream_id, headers, end_stream)
    
    def send_raw_headers_frame(self, stream_id: int, headers: Headers, end_stream: bool = False) -> None:
        """
        Send a HEADERS frame with raw header encoding, bypassing QPACK compression.
        This allows headers to be sent in arbitrary order for non-conformance testing.
        
        :param stream_id: The stream ID to send the frame on
        :param headers: The headers to send (in the exact order provided)
        :param end_stream: Whether to end the stream
        """
        # Create a simple encoder for raw header encoding without compression
        encoder = pylsqpack.Encoder()
        
        # Encode headers without compression (table size 0)
        encoder_updates, frame_data = encoder.encode(stream_id, headers)
        
        # Send encoder updates if any (usually none for simple encoding)
        if encoder_updates and self._manual_encoder_stream_id:
            self._quic.send_stream_data(self._manual_encoder_stream_id, encoder_updates)
        
        # Create and send the HEADERS frame
        encoded_frame = encode_frame(FrameType.HEADERS, frame_data)
        self._quic.send_stream_data(stream_id, encoded_frame, end_stream)
    
    def send_data_frame(self, stream_id: int, data: bytes, end_stream: bool = False) -> None:
        """
        Send a DATA frame on the specified stream.
        
        :param stream_id: The stream ID to send the frame on
        :param data: The data to send
        :param end_stream: Whether to end the stream
        """
        self._h3.send_data(stream_id, data, end_stream)
    
    def send_max_push_id_frame(self, stream_id: int, max_push_id: int) -> None:
        """
        Send a MAX_PUSH_ID frame on the specified stream.
        
        :param stream_id: The stream ID to send the frame on (typically control stream)
        :param max_push_id: The maximum push ID value
        """
        frame_data = encode_uint_var(max_push_id)
        encoded_frame = encode_frame(FrameType.MAX_PUSH_ID, frame_data)
        
        self._quic.send_stream_data(stream_id, encoded_frame)
    
    def send_raw_frame(self, stream_id: int, frame_type: int, frame_data: bytes) -> None:
        """
        Send a raw frame with arbitrary type and data.
        
        :param stream_id: The stream ID to send the frame on
        :param frame_type: The frame type
        :param frame_data: The frame payload
        """
        encoded_frame = encode_frame(frame_type, frame_data)
        self._quic.send_stream_data(stream_id, encoded_frame)
    
    def send_goaway_frame(self, stream_id: int, stream_or_push_id: int) -> None:
        """
        Send a GOAWAY frame on the specified stream.
        
        :param stream_id: The stream ID to send the frame on
        :param stream_or_push_id: The ID to include in the GOAWAY frame
        """
        frame_data = encode_uint_var(stream_or_push_id)
        encoded_frame = encode_frame(FrameType.GOAWAY, frame_data)
        
        self._quic.send_stream_data(stream_id, encoded_frame)
    
    def get_control_stream_id(self) -> Optional[int]:
        """Get the manually created control stream ID."""
        return self._manual_control_stream_id
    
    def get_encoder_stream_id(self) -> Optional[int]:
        """Get the manually created encoder stream ID."""
        return self._manual_encoder_stream_id
    
    def get_decoder_stream_id(self) -> Optional[int]:
        """Get the manually created decoder stream ID."""
        return self._manual_decoder_stream_id
    
    @property
    def connection(self) -> H3Connection:
        """Get the underlying H3Connection for advanced operations."""
        return self._h3 