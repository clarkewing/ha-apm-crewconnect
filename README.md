<div align="center">
  <a href="https://github.com/ShaanCoding/ReadME-Generator">
    <img src="https://brands.home-assistant.io/apm/icon@2x.png" alt="APM CrewConnect logo" width="80" height="80">
  </a>
  <h3 align="center">APM CrewConnect for Home Assistant</h3>
  <p align="center">
    Tie your airline roster into Home Assistant!
    <br/>
    <br/>
    <a href="https://github.com/clarkewing/ha-apm-crewconnect"><strong>Explore the docs »</strong></a>
    <br/>
    <br/>
    <div>
      <a href="https://github.com/clarkewing/ha-apm-crewconnect/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
      <a href="https://github.com/clarkewing/ha-apm-crewconnect/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
    </div>
  </p>
</div>


## About The Project
Home Assistant has allowed me to automate tons of things inside my home, but I've always found it more adapted to the "classic" 9-to-5 weekday and weekend routines most people have.

Working within an airline, I wanted to integrate my often complex and varied roster into my smart home. This integration aims to do just that, with nifty little tools to simplify management of Home Assistant around my airline roster.


### Built With
Many different open source projects made this one possible, and here they are showcased below.

- [Home Assistant](https://www.home-assistant.io)
- [APM CrewConnect (Python SDK)](https://github.com/clarkewing/apm_crewconnect)


### Installation
1. Install files  
    Download the [latest release](https://github.com/clarkewing/ha-apm-crewconnect/releases) as a zip file and extract it into the `custom_components` folder in your HA installation.
2. Restart Home Assistant to load the integration.
3. Go to Configuration -> Integrations and click the big orange '+' button. Look for APM CrewConnect and click to add it.
4. The UI will prompt you for your APM host.  
    _The host can be found by navigating to your APM mobile app settings and looking for the "Service URL"._
5. The configuration flow will provide you with a URL to login using OKTA (the only currently supported login option).  
    Open the provided URL in Chrome [with the console open](https://support.google.com/docs/thread/1873663/collecting-console-logs-chrome-browser-only?hl=en) and log into your account. The console should log an error saying that Chrome was unable to redirect you to a URL starting with `com.apm.crewconnect:/`.  
    Copy and paste this authentication redirect URL into the integration configuration flow.
6. The integration should now be configured properly!


## Usage
### Finding unstaffed flights
The `apm.find_unstaffed_flights` service allows you to search the flight schedule for unstaffed flights. You can filter by date, aircraft (73H or 32N), and role code (CDB, OPL, TRI, CC, CA, or INS).


## Roadmap
- [ ] Add Changelog
- [ ] Add Issue Templates
- [ ] Add Calendar Entity with roster
  - [ ] Add dedicated calendar services for easier automations.
- [ ] Multi-language Support
  - [ ] French

See the [open issues](https://github.com/clarkewing/ha-apm-crewconnect/issues) for a full list of proposed features (and known issues).


## Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this integration better, please fork the repository and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/amazing-feature`)
3. Commit your Changes (`git commit -m 'Add some Amazing Feature'`)
4. Push to the Branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## License
Distributed under the MIT License. See [MIT License](https://opensource.org/licenses/MIT) for more information.
