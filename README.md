# BJJ Match Study

A web application for studying Brazilian Jiu-Jitsu competition matches with detailed technical analysis and breakdowns.

## Features

- Comprehensive collection of BJJ competition matches
- Detailed technical analysis of each match including:
  - Key positions and transitions
  - Submission attempts
  - Strategic breakdowns
  - Timestamped events
- Advanced search and filtering:
  - Search by competitor names
  - Filter by positions
  - Filter by techniques
  - Filter by submissions
- Mobile-responsive design
- YouTube integration for match playback

## Current Collection

- The IBJJF Crown 2024
- European Championship 2024
- Pan Championship 2023
- World Championship 2021

## Technical Details

- Built with vanilla JavaScript and HTML/CSS
- Static site hosted on GitHub Pages
- Markdown-based content for easy updates
- YouTube iframe API for video playback

## Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/bjj-match-study.git
   cd bjj-match-study
   ```

2. Run a local server:
   ```bash
   python -m http.server 8000
   ```

3. Open `http://localhost:8000` in your browser

## Adding a match

1. Drop a new markdown file in `analysis/` following the format of an existing
   match (see `analysis/Tainan-Dalpra-vs-Elijah-Dorsey_The-IBJJF-Crown-2024.md`
   for reference). Required sections: `## Match Details`, `## Fight Breakdown`,
   `## Label List`.
2. Regenerate the match manifest that the site loads:
   ```bash
   python scripts/build_manifest.py
   ```
3. Commit both the new `.md` file and the updated `analysis/index.json`.

CI runs `python scripts/build_manifest.py --check` on every PR and fails if the
committed manifest is out of date.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for any purpose.
