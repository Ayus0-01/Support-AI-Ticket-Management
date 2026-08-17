from django.test import SimpleTestCase
from .classification.embeddings import generate_embedding

from .classification.preprocessing import (
    remove_quoted_replies,
    remove_signature,
    mask_pii,
    preprocess_ticket,
)
from .classification.features import (
    has_error_code,
    extract_keyword_flags,
    extract_features,
)


class PreprocessingTests(SimpleTestCase):

    def test_remove_quoted_reply(self):
        text = """VPN is not connecting.

> Previous message
> VPN worked yesterday.

Thanks"""

        result = remove_quoted_replies(text)

        self.assertNotIn("> Previous message", result)
        self.assertIn("VPN is not connecting.", result)

    def test_remove_signature(self):
        text = """VPN is not connecting.

Regards,
Ayusman"""

        result = remove_signature(text)

        self.assertIn("VPN is not connecting.", result)
        self.assertNotIn("Ayusman", result)

    def test_mask_pii(self):
        text = """
        Email: ayusman@gmail.com
        IP: 192.168.1.25
        Password is MySecret123
        """

        result = mask_pii(text)

        self.assertIn("[EMAIL]", result)
        self.assertIn("[IP]", result)
        self.assertIn("[PASSWORD]", result)

        self.assertNotIn("ayusman@gmail.com", result)
        self.assertNotIn("192.168.1.25", result)
        self.assertNotIn("MySecret123", result)

    def test_full_preprocessing(self):
        subject = "VPN connection failing"

        description = """Unable to connect to VPN.

Email: ayusman@gmail.com
IP: 192.168.1.25

Regards,
Ayusman

> Previous conversation
> VPN worked yesterday.
"""

        result = preprocess_ticket(subject, description)

        self.assertEqual(
            result["subject"],
            "VPN connection failing"
        )

        self.assertIn(
            "Unable to connect to VPN.",
            result["description"]
        )

        self.assertIn("[EMAIL]", result["description"])
        self.assertIn("[IP]", result["description"])

        self.assertNotIn(
            "Previous conversation",
            result["description"]
        )


class FeatureExtractionTests(SimpleTestCase):

    def test_error_code_detection(self):
        self.assertTrue(
            has_error_code(
                "VPN failed with error code ERR-1234"
            )
        )

    def test_error_code_not_present(self):
        self.assertFalse(
            has_error_code(
                "VPN connection is not working"
            )
        )

    def test_keyword_flags(self):
        flags = extract_keyword_flags(
            "Unable to connect to VPN using AnyConnect"
        )

        self.assertTrue(flags["vpn"])
        self.assertTrue(flags["network"])
        self.assertFalse(flags["security"])

    def test_feature_extraction(self):
        features = extract_features(
            subject="VPN connection failing",
            description="Unable to connect to company VPN.",
            department="Finance",
            channel="portal",
            affected_scope="TEAM",
            work_blocked="YES",
        )

        self.assertEqual(
            features["department"],
            "Finance"
        )

        self.assertEqual(
            features["channel"],
            "portal"
        )

        self.assertEqual(
            features["affected_scope"],
            "TEAM"
        )

        self.assertEqual(
            features["work_blocked"],
            "YES"
        )

        self.assertTrue(
            features["keyword_flags"]["vpn"]
        )

        self.assertIsNone(
            features["embedding"]
        )

class EmbeddingTests(SimpleTestCase):

    def test_embedding_generation(self):
        embedding = generate_embedding(
            subject="VPN connection failing",
            description="Unable to connect to the company VPN.",
        )

        self.assertIsInstance(
            embedding,
            list
        )

        self.assertEqual(
            len(embedding),
            384
        )

        self.assertTrue(
            all(
                isinstance(value, float)
                for value in embedding
            )
        )