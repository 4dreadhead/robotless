import hashlib
import time
import json
from src.utils.bytes_to_integer import BytesToInteger


class TLSParser:
    TIMESTAMP_KEY = "timestamp"
    GREASE_TABLE = {
        0x0a0a: True, 0x1a1a: True, 0x2a2a: True, 0x3a3a: True,
        0x4a4a: True, 0x5a5a: True, 0x6a6a: True, 0x7a7a: True,
        0x8a8a: True, 0x9a9a: True, 0xaaaa: True, 0xbaba: True,
        0xcaca: True, 0xdada: True, 0xeaea: True, 0xfafa: True
    }

    def __init__(self, bytes_raw):
        self.bytes_raw_original = bytes_raw
        self.bytes_raw = BytesToInteger(bytes_raw)
        self.cached = None

    def as_json(self):
        return self.cached if self.cached else self.collect_info().cached

    def as_str(self):
        return json.dumps(self.as_json())

    def collect_info(self):
        parsed_client_hello = self.parse_client_hello()

        ja3, ja3_normalized = self.collect_ja3(parsed_client_hello)

        self.cached = {
            "ja3_hash": hashlib.md5(ja3.encode()).hexdigest(),
            "ja3_text": ja3,
            "ja3n_hash": hashlib.md5(ja3_normalized.encode()).hexdigest(),
            "ja3n_text": ja3_normalized,
            self.TIMESTAMP_KEY: int(time.time())
        }

        return self

    def parse_client_hello(self):
        data = self.bytes_raw

        content_type, data = data.take(1)
        version, data = data.take(2)
        length, data = data.take(2)
        handshake_type, data = data.take(1)

        if content_type != 22:
            raise ValueError("This is not a tls content.")

        if handshake_type != 1:
            raise ValueError("This is not client_hello handshake.")

        client_hello_length, data = data.take(3)
        legacy_version, data = data.take(2)
        client_random, data = data.take(32)

        legacy_session_id_len, data = data.take(1)
        legacy_session_id, data = data.take(legacy_session_id_len)

        cipher_suites_length, data = data.take(2)
        cipher_suites = [data[i:i+2].to_i for i in range(0, cipher_suites_length, 2)]
        _, data = data.take(cipher_suites_length)

        legacy_compression_methods, data = data.take(2)

        extensions_length, data = data.take(2)
        taken_size = 0
        extensions = []
        while data:
            if taken_size > extensions_length:
                raise ValueError(f"Got more bytes than extensions length.")

            extension_type, data = data.take(2)
            extension_length, data = data.take(2)
            extension_content_raw = data[:extension_length]
            extension_content, data = data.take(extension_length)
            ext_data = self.parse_extension(extension_type, extension_length, extension_content_raw)

            taken_size += 4 + extension_length

            extensions.append({
                "value": extension_type,
                "length": extension_length,
                "data": ext_data
            })

        return {
            "content_type": content_type,
            "version": version,
            "length": length,
            "handshake_type": handshake_type,
            "client_hello_length": client_hello_length,
            "legacy_version": legacy_version,
            "random": client_random,
            "legacy_session_id_len": legacy_session_id_len,
            "legacy_session_id": legacy_session_id,
            "cipher_suites_length": cipher_suites_length,
            "cipher_suites": cipher_suites,
            "legacy_compression_methods": legacy_compression_methods,
            "extensions_length": extensions_length,
            "extensions": extensions
        }

    @staticmethod
    def parse_extension(ext_type, ext_len, ext_raw):
        if ext_len != len(ext_raw):
            raise ValueError(f"Extension {ext_type} have a wrong size: {ext_len} from header, {len(ext_raw)} in fact")

        if ext_len == 0:
            return 0

        ext_list = []
        ext_list_size = 0

        for i in range(2):
            list_size = ext_raw[0:i+1].to_i

            if list_size == len(ext_raw[i+1:]):
                ext_list_size, ext_raw = ext_raw.take(i + 1)
                break

        if ext_list_size == 0:
            return ext_raw.to_i

        taken_size = 0

        while ext_raw:
            if taken_size > ext_list_size:
                raise ValueError(f"Got more bytes at keys extension.")

            match ext_type:
                case 51:
                    key_group, ext_raw = ext_raw.take(2)
                    key_size, ext_raw = ext_raw.take(2)
                    key, ext_raw = ext_raw.take(key_size)

                    taken_size += 4 + key_size

                    ext_list.append({
                        "key_group": key_group,
                        "key_size": key_size,
                        "key": key
                    })
                case 11:
                    element, ext_raw = ext_raw.take(1)
                    ext_list.append(element)

                    taken_size += 1
                case _:
                    element, ext_raw = ext_raw.take(2)
                    ext_list.append(element)

                    taken_size += 2

        return ext_list

    def collect_ja3(self, client_hello):
        version = [client_hello.get("version") or client_hello.get("legacy_version")]
        cipher_suites = self.grease_filter(client_hello["cipher_suites"])
        extensions = self.grease_filter(ext["value"] for ext in client_hello["extensions"])
        supported_groups_all = self.data_by_ext_value(10, client_hello["extensions"])
        supported_groups = self.grease_filter(supported_groups_all)
        ec_curves_point_formats = self.data_by_ext_value(11, client_hello["extensions"])

        ja3_fingerprint = [version, cipher_suites, extensions, supported_groups, ec_curves_point_formats]
        ja3 = self.generate_ja3_string(ja3_fingerprint)

        ja3_fingerprint[2].sort()
        ja3_normalized = self.generate_ja3_string(ja3_fingerprint)

        return ja3, ja3_normalized

    def grease_filter(self, data):
        return [obj for obj in data if not self.GREASE_TABLE.get(obj, False)]

    @staticmethod
    def data_by_ext_value(value, data, default=()):
        return next((obj["data"] for obj in data if obj["value"] == value), default)

    @staticmethod
    def generate_ja3_string(fingerprint):
        return ",".join("-".join(map(str, obj)) for obj in fingerprint)
