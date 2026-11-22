import base64, tempfile, unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch
from verifier.trusted_timestamp import verify_receipt_signature_timestamp
from verifier.verify import CordValidationError

ENV={"spec_version":"0.1","alg":"Ed25519","key_id":"test","signature":base64.b64encode(b"s"*64).decode("ascii")}

class TrustedTimestampTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.ca=Path(self.tmp.name)/"ca.pem"
        self.ca.write_text("placeholder",encoding="ascii")
    def tearDown(self): self.tmp.cleanup()

    @patch("verifier.trusted_timestamp.shutil.which",return_value="/usr/bin/openssl")
    @patch("verifier.trusted_timestamp.subprocess.run")
    def test_pass_binds_exact_signature_bytes(self,run,_which):
        captured = {}
        def fake_run(args, **kwargs):
            if "-verify" in args:
                captured["data"] = Path(args[args.index("-data")+1]).read_bytes()
                captured["shell"] = kwargs["shell"]
                return CompletedProcess(args,0,"Verification: OK","")
            return CompletedProcess(args,0,"Time stamp: Nov 22 12:34:56 2026 GMT","")
        run.side_effect=fake_run
        result=verify_receipt_signature_timestamp(b"DER",ENV,self.ca)
        self.assertEqual(result["generation_time"],"2026-11-22T12:34:56Z")
        self.assertEqual(captured["data"],b"s"*64)
        self.assertFalse(captured["shell"])

    @patch("verifier.trusted_timestamp.shutil.which",return_value="/usr/bin/openssl")
    @patch("verifier.trusted_timestamp.subprocess.run")
    def test_bad_token_fails(self,run,_which):
        run.return_value=CompletedProcess([],1,"","bad imprint")
        with self.assertRaisesRegex(CordValidationError,"validation failed"):
            verify_receipt_signature_timestamp(b"DER",ENV,self.ca)

    def test_bad_signature_and_token_rejected(self):
        with self.assertRaisesRegex(CordValidationError,"64 bytes"):
            verify_receipt_signature_timestamp(b"x",dict(ENV,signature=base64.b64encode(b"x").decode()),self.ca)
        with self.assertRaisesRegex(CordValidationError,"non-empty"):
            verify_receipt_signature_timestamp(b"",ENV,self.ca)

    def test_missing_ca_rejected(self):
        with self.assertRaisesRegex(CordValidationError,"CA file does not exist"):
            verify_receipt_signature_timestamp(b"x",ENV,Path(self.tmp.name)/"missing")

    @patch("verifier.trusted_timestamp.shutil.which",return_value=None)
    def test_openssl_required(self,_which):
        with self.assertRaisesRegex(CordValidationError,"not found"):
            verify_receipt_signature_timestamp(b"x",ENV,self.ca)

    @patch("verifier.trusted_timestamp.shutil.which",return_value="/usr/bin/openssl")
    @patch("verifier.trusted_timestamp.subprocess.run")
    def test_bad_generation_time_rejected(self,run,_which):
        run.side_effect=[CompletedProcess([],0,"OK",""),CompletedProcess([],0,"no time","")]
        with self.assertRaisesRegex(CordValidationError,"generation time"):
            verify_receipt_signature_timestamp(b"x",ENV,self.ca)

if __name__=="__main__": unittest.main()
