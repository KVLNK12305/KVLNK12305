<table border="0" width="100%">
  <tr>
    <td width="300" align="center" valign="middle">
      <img src="./ascii.svg" width="270" alt="Kushal Kurapati"/>
    </td>
    <td valign="middle" align="left">
      <h1>Kushal Kurapati</h1>
      CS engineering student at Amrita Vishwa Vidyapeetham and part of Init Club's research group.
      <br><br>
      I like understanding what's happening below the framework layer: bytes on the wire, processes, memory. Most of my projects are defensive security, cloud forensics and protocol tooling, mainly in Rust, Go and Python. Lately I've been reverse-engineering a Bluetooth protocol, building an identity gateway for machine-to-machine traffic, and writing tools that reconstruct what happened during cloud incidents.
      <br><br>
      <a href="https://www.linkedin.com/in/venkata-lakshmi-narasimha-kushal-kurapati-729ab4289/">LinkedIn</a> · <a href="https://leetcode.com/u/kurapatikushalnarasimha95/">LeetCode</a> · <a href="mailto:kls2edmentre@gmail.com">Email</a>
    </td>
  </tr>
</table>

## Projects

### [GhostShell](https://github.com/KVLNK12305/GhostShell)
`Rust` `Linux`

A defensive daemon for Linux hosts. It watches active TCP/UDP sockets, process lineage (for example a shell spawned under a web server, or cryptominer behaviour) and authentication logs. When an anomaly crosses its threshold, it can terminate the offending process and export encrypted threat logs.

*Status: runs as a daemon, with an integration test suite.*

### [Akira](https://github.com/KVLNK12305/Akira)
`Rust` `Bun` `React`

An identity gateway for non-human identities (service accounts, API clients), aimed at payment systems. It verifies sessions cryptographically, uses Argon2id and MFA patterns based on NIST 800-63 guidance, and scores each request against a learned baseline. Machine credentials that deviate on IP, scope or request velocity are quarantined automatically.

*Status: working prototype with a React dashboard and an attack simulator.*

### [KlaudTrace](https://github.com/KVLNK12305/KlaudTrace)
`Go` `AWS`

Reconstructs what happened during an incident in an AWS environment. It follows events through asynchronous pipelines across services to work out what changed, where state drifted, and how far the damage spread.

*Status: in active development.*

### [TuneDeck](https://github.com/KVLNK12305/TuneDeck)
`Python` `Textual`

A keyboard-driven terminal app and CLI for controlling JBL Bluetooth devices from Linux. It talks to the device over RFCOMM using Airoha's RACE protocol, covering ANC, Ambient Aware, TalkThru, multi-band EQ, battery readouts (left, right and case) and power off. A `--sim` mode with sample device models lets you try it without hardware.

*Status: working, tested on a JBL Tune 770NC.*

### [CloudPulse](https://github.com/KVLNK12305/CloudPulse)
`Python` `Azure`

Looks at security posture and cloud spend together. It evaluates resource graphs and telemetry to give each resource a combined risk score, and supports human-approved remediations such as changing an open NSG inbound rule from Allow to Deny or isolating a workload.

*Status: offline demo on seeded telemetry. The Azure test environment was shut down to avoid ongoing costs.*

### [K.A.I.R.O](https://github.com/KVLNK12305/K.A.I.R.O)
`Dart` `Flutter`

A personal planner built around the idea that a week is a fixed budget of 168 hours. It tracks where time goes, maps energy peaks, and logs expenses captured through background broadcast receivers. Built with Material 3, Isar for the on-device database, and Riverpod.

*Status: working app, running on-device.*

## Stack

**Languages:** Rust · Go · Python · TypeScript · Dart · C · C++
**Cloud:** AWS · Azure · Docker
**Tools:** Wireshark · gdb · Bluetooth RFCOMM · Bun · React · Flutter
