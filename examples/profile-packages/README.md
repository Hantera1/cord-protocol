# Initial CORD profile examples

The repository contains draft evidence examples for:

- `luxury-asset`: an asset registration record plus an explicitly unassessed authenticity record.
- `clock`: a producer-declared time claim, a clock observation with unknown synchronization state, and a per-source sequence record.

These examples are deliberately non-authoritative. They do not claim that an asset is genuine, that a person owns it, or that any timestamp is trusted.

Build complete Core + profile packages:

```bash
python -m pip install -r requirements.txt
python examples/build_profile_packages.py --output-dir ./build/profile-packages
```

Verify both packages offline against the repository's locally pinned profile registry:

```bash
python verifier/profile_engine.py ./build/profile-packages/luxury-asset --registry ./profiles
python verifier/profile_engine.py ./build/profile-packages/clock --registry ./profiles
```

The local registry and pinned profile files are trust inputs. Protect and distribute them through an authenticated process in real deployments.
