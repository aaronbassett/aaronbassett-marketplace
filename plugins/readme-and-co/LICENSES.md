# License Selection Guide

Comprehensive guide for selecting appropriate licenses for your project.

## Quick Decision Tree

### For Code Projects

```
Do you want maximum adoption?
├─ YES → MIT License (most popular, permissive)
└─ NO  → Do you need patent protection?
    ├─ YES → Apache-2.0 (explicit patent grant)
    └─ NO  → Do you want copyleft?
        ├─ YES → Is this a network service?
        │   ├─ YES → AGPL-3.0 (network copyleft)
        │   └─ NO  → GPL-3.0 (strong copyleft)
        └─ NO  → Is this a commercial SaaS?
            ├─ YES → FSL-1.1-MIT (2yr delay, then MIT)
            └─ NO  → Review full list below
```

### For Documentation/Media

```
Should others give attribution?
├─ NO  → CC0-1.0 (public domain dedication)
└─ YES → Should derivative works also be open?
    ├─ YES → CC-BY-SA-4.0 (ShareAlike/copyleft)
    └─ NO  → Should commercial use be allowed?
        ├─ YES → CC-BY-4.0 (most permissive with attribution)
        └─ NO  → CC-BY-NC-4.0 (non-commercial restriction)
```

## Available Licenses

### GitHub-Approved Licenses (Tier 1 for Code)

These 13 licenses are recommended first for code projects:

| License | Category | Best For | Patent Grant | Copyleft |
|---------|----------|----------|--------------|----------|
| **MIT** | Permissive | Maximum adoption, simple projects | No | No |
| **Apache-2.0** | Permissive | Patent-sensitive projects | Yes | No |
| **GPL-3.0** | Copyleft | Prevent proprietary forks | Yes | Strong |
| **AGPL-3.0** | Copyleft | Prevent proprietary SaaS | Yes | Network |
| **BSD-3-Clause** | Permissive | Academic, trademark protection | No | No |
| **BSD-2-Clause** | Permissive | Simpler BSD | No | No |
| **MPL-2.0** | Weak Copyleft | Libraries, file-level copyleft | Yes | File-level |
| **LGPL-2.1** | Weak Copyleft | Libraries with GPL compatibility | Yes | Library |
| **EPL-2.0** | Weak Copyleft | Eclipse ecosystem | Yes | Weak |
| **BSL-1.0** | Permissive | Boost libraries | No | No |
| **Unlicense** | Public Domain | Dedicate to public domain | No | No |
| **GPL-2.0** | Copyleft | Legacy projects (prefer GPL-3.0) | No | Strong |
| **CC0-1.0** | Public Domain | Public domain dedication | No | No |

### Creative Commons Licenses (Tier 1 for Non-Code)

These 7 licenses are recommended for documentation, media, and content:

| License | Attribution | ShareAlike | Commercial | Derivatives | Best For |
|---------|-------------|------------|------------|-------------|----------|
| **CC-BY-4.0** | Yes | No | Yes | Yes | Documentation, most permissive |
| **CC-BY-SA-4.0** | Yes | Yes | Yes | Yes | Wikipedia-style, viral sharing |
| **CC-BY-NC-4.0** | Yes | No | No | Yes | Non-commercial content |
| **CC-BY-NC-SA-4.0** | Yes | Yes | No | Yes | Non-commercial + ShareAlike |
| **CC-BY-ND-4.0** | Yes | No | Yes | No | No derivatives allowed |
| **CC-BY-NC-ND-4.0** | Yes | No | No | No | Most restrictive CC |
| **CC0-1.0** | No | No | Yes | Yes | Public domain, like Unlicense |

### FSL-1.1-MIT (Time-Delayed Open Source)

**Functional Source License with MIT Future License**

- **Category**: Time-delayed open source
- **OSI Approved**: No (but ethical and sustainable)
- **Used by**: Sentry, GitButler, and other commercial OSS companies

**How it works**:
1. Source code is available immediately (source-available)
2. Production use is restricted for 2 years from release
3. After 2 years, automatically becomes MIT license
4. Users can read, modify, test immediately
5. Cannot use in production or competing services during restriction period

**When to use**:
- Commercial SaaS products
- Projects wanting eventual open source with revenue window
- "Open source with a business model" approach

**Template**: `templates/LICENSE/fsl/FSL-1.1-MIT.template.md`

## License Characteristics

### Permissions

What you can do with the code:

| Permission | MIT | Apache-2.0 | GPL-3.0 | AGPL-3.0 | FSL-1.1-MIT | CC-BY-4.0 |
|------------|-----|------------|---------|----------|-------------|-----------|
| Commercial use | ✓ | ✓ | ✓ | ✓ | Limited* | ✓ |
| Modifications | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Distribution | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Patent use | — | ✓ | ✓ | ✓ | — | — |
| Private use | ✓ | ✓ | ✓ | ✓ | ✓ | — |

*FSL: Production use restricted for 2 years, then becomes MIT

### Conditions

What you must do:

| Condition | MIT | Apache-2.0 | GPL-3.0 | AGPL-3.0 | FSL-1.1-MIT | CC-BY-4.0 |
|-----------|-----|------------|---------|----------|-------------|-----------|
| Include license | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Include copyright | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| State changes | — | ✓ | ✓ | ✓ | — | — |
| Disclose source | — | — | ✓ | ✓ | ✓ | — |
| Same license | — | — | ✓ (copyleft) | ✓ (network) | — | — |

### Limitations

What the license disclaims:

| Limitation | MIT | Apache-2.0 | GPL-3.0 | AGPL-3.0 | CC-BY-4.0 |
|------------|-----|------------|---------|----------|-----------|
| Liability | ✓ | ✓ | ✓ | ✓ | ✓ |
| Warranty | ✓ | ✓ | ✓ | ✓ | ✓ |
| Trademark use | — | ✓ | — | — | ✓ |
| Patent use** | — | ✓ | — | — | — |

**Apache-2.0 includes patent retaliation clause

## License Selection by Project Type

### Open Source Library

**First choice**: MIT
- Widely accepted, maximum adoption
- No surprises for users

**If patent concerns**: Apache-2.0
- Explicit patent grant and retaliation
- Protects against patent trolls

**If want copyleft**: LGPL-2.1
- Library-specific copyleft
- Allows proprietary apps to use library

### Open Source Application

**User preference**: MIT or GPL-3.0
- MIT for permissive
- GPL for preventing proprietary forks

**If network service**: AGPL-3.0
- Prevents proprietary SaaS without source sharing
- Strongest copyleft

### Commercial SaaS

**First choice**: FSL-1.1-MIT
- Revenue window (2 years)
- Automatic MIT transition
- Sentry model

**Alternative**: Dual GPL-3.0 + Commercial
- GPL for open source users
- Commercial license for proprietary use

### Documentation/Tutorials

**First choice**: CC-BY-4.0
- Attribution required
- Commercial use allowed
- Most permissive with credit

**If want ShareAlike**: CC-BY-SA-4.0
- Like GPL for content
- Derivatives must use same license

**If public domain**: CC0-1.0
- No restrictions
- Like Unlicense for content

### Internal/Private Projects

**Not needed**: No license required for private repos

**If planning to open source**: Choose license early
- Easier than retrofitting later
- Sets expectations for contributors

## Multi-Licensing

### What is Multi-Licensing?

Offering the same software under multiple license options, allowing users to choose which terms they prefer.

### Common Patterns

**1. Permissive + Copyleft**
```
Example: MIT + GPL-3.0
Users choose which license they prefer
```

**2. Open Source + Commercial**
```
Example: GPL-3.0 + Proprietary
- GPL for open source users (must share modifications)
- Commercial license for proprietary use (pay for closed-source)
Business model: "Open core" or dual licensing
```

**3. Time-Delayed**
```
Example: FSL-1.1-MIT
- FSL now (restricted production use)
- Automatic MIT after 2 years
No user choice needed, automatic transition
```

### When to Use Multi-Licensing

**Good for**:
- Commercial open-source projects needing revenue
- Projects wanting copyleft without scaring permissive-only users
- Balancing community and business needs

**Business models**:
- **Open Core**: Base features under OSS, premium under commercial
- **Dual Licensing**: GPL for OSS, commercial for proprietary
- **Time-Delayed**: FSL → MIT automatic transition

### Multi-License File Structure

**Option 1: Dual GPL + Commercial**
```
repository/
├── LICENSE (GPL-3.0)
├── LICENSE.commercial (or link to purchase)
└── README.md (explains dual licensing)
```

README section:
```markdown
## License

This project is dual-licensed:

- **Open Source**: GNU General Public License v3.0 (GPL-3.0)
  - Free for open source projects
  - Derivatives must also be GPL-3.0

- **Commercial**: Proprietary commercial license
  - For use in proprietary/closed-source products
  - Contact: sales@example.com

Choose the license that fits your use case.
```

**Option 2: FSL (Single License, Time-Based)**
```
repository/
├── LICENSE.md (FSL-1.1-MIT, includes both licenses)
└── README.md (explains automatic MIT transition)
```

## License Education

### MIT License

**What**: Most popular open source license, very permissive

**Allows**:
- Commercial use
- Modifications
- Distribution
- Private use

**Requires**:
- Include license and copyright notice

**Good for**: Maximum adoption, simple projects, most cases

**Not good for**: Patent protection, preventing proprietary forks

### Apache-2.0 License

**What**: Permissive license with explicit patent grant

**Allows**:
- Everything MIT allows
- Plus: explicit patent rights

**Requires**:
- Include license and copyright
- State changes made to code
- Include NOTICE file if present

**Good for**: Patent-sensitive projects, larger organizations, projects with novel algorithms

**Not good for**: Simplicity (more complex than MIT)

### GPL-3.0 License

**What**: Strong copyleft, derivatives must be GPL

**Allows**:
- Commercial use
- Modifications
- Distribution
- Patent use

**Requires**:
- Disclose source code
- Include license and copyright
- State changes
- Use same license (copyleft)

**Good for**: Preventing proprietary forks, ensuring freedom, community-driven projects

**Not good for**: Maximum adoption (some avoid GPL), proprietary integration

### AGPL-3.0 License

**What**: GPL + network provision (SaaS loophole closed)

**Everything GPL-3.0 plus**:
- Network use triggers copyleft
- Running as a service counts as distribution

**Good for**: Preventing proprietary SaaS, ensuring server-side code stays open

**Not good for**: SaaS companies (by design), maximum adoption

### FSL-1.1-MIT

**What**: Commercial now, open source (MIT) in 2 years

**Timeline**:
- Year 0: Release under FSL-1.1-MIT
- Years 0-2: Source available, production use restricted
- Year 2+: Automatic MIT license

**Allows** (immediately):
- Read and study code
- Modify for internal use
- Test and develop

**Restricts** (for 2 years):
- Production use
- Competing services

**Good for**: Commercial SaaS, sustainable open source, Sentry model

**Not good for**: Immediate production use by others, traditional open source

### Creative Commons BY-4.0

**What**: Attribution-only license for content

**Allows**:
- Share and adapt
- Commercial use
- Any medium/format

**Requires**:
- Give attribution
- Link to license
- Indicate if changes made

**Good for**: Documentation, blog posts, tutorials, educational content

**Not good for**: Code (use OSI licenses), preventing commercial use

## Additional Resources

### License Summaries

For plain-English explanations:
- [tldrlegal.com](https://www.tldrlegal.com/) - All major licenses explained
- GitHub's [choosealicense.com](https://choosealicense.com/) - Simple license chooser
- [opensource.org/licenses](https://opensource.org/licenses) - OSI-approved licenses

### Multi-Licensing Resources

- [FOSSA: Dual Licensing Models Explained](https://fossa.com/blog/dual-licensing-models-explained/)
- [Milvus: What is Dual Licensing](https://milvus.io/ai-quick-reference/what-is-dual-licensing-in-opensource-projects)
- [FSL Software](https://fsl.software/) - Functional Source License

### License APIs

- GitHub Licenses API: `https://api.github.com/licenses`
- SPDX License List: `https://spdx.org/licenses/licenses.json`
- Creative Commons API: Various endpoints per license

## Using Licenses in Your Project

### Create LICENSE File

```bash
python scripts/populate_license.py \
  --license MIT \
  --holder "Your Name" \
  --year 2026 \
  --output LICENSE
```

### Refresh License Templates

```bash
python scripts/fetch_licenses.py
```

(Only needed if licenses change - very rare)

### License in README

Add license badge and section:

```markdown
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

For multi-licensing:

```markdown
## License

This project is dual-licensed under your choice of:
- [MIT License](LICENSE-MIT) for permissive use
- [Apache-2.0 License](LICENSE-APACHE) for patent protection

See [LICENSING.md](LICENSING.md) for details.
```

## License Compatibility

When using dependencies or combining code:

### GPL Compatibility

GPL requires all combined code to be GPL:
- GPL + MIT = GPL (GPL is viral)
- GPL + Apache = GPL
- GPL + Proprietary = ❌ Incompatible

### MIT Compatibility

MIT is compatible with almost everything:
- MIT + Apache = Apache
- MIT + GPL = GPL
- MIT + Proprietary = ✓ Compatible

### Apache Compatibility

Apache is widely compatible:
- Apache + MIT = Apache
- Apache + GPL-3.0 = GPL-3.0 (but check GPL-2.0 incompatibility)
- Apache + Proprietary = ✓ Compatible

## Common Mistakes to Avoid

❌ **Using GPL when you want permissive**
- GPL is copyleft, not permissive
- Use MIT or Apache-2.0 instead

❌ **No license at all**
- Default is "all rights reserved"
- Add a license even for experiments

❌ **Changing licenses frequently**
- Confuses users and contributors
- Consider multi-licensing instead

❌ **Using Creative Commons for code**
- CC licenses aren't designed for software
- Use OSI-approved licenses for code

❌ **Not understanding copyleft**
- GPL requires derivatives to be GPL
- Can prevent some adoption

✓ **Do this instead**:
- Choose license early
- Use this guide's decision tree
- Stick with your choice
- Document clearly in README

## Quick Reference

**Most common choices**:
- **Libraries**: MIT (or Apache-2.0 for patents)
- **Applications**: MIT or GPL-3.0 (user preference)
- **Network services**: AGPL-3.0 (prevent proprietary SaaS)
- **Commercial SaaS**: FSL-1.1-MIT (delay + MIT)
- **Documentation**: CC-BY-4.0 (attribution)
- **Public domain**: CC0-1.0 or Unlicense

**When unsure**: MIT (safest default for code)
