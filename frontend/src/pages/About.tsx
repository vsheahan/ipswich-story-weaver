export default function About() {
  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <h2 className="text-2xl font-serif text-sea-800 mb-8">How This Works</h2>

      <div className="prose prose-sea font-serif text-gray-700 space-y-6">
        <section>
          <h3 className="text-lg font-semibold text-sea-700 mb-3">
            Fiction Grounded in Fact
          </h3>
          <p>
            The stories you read here are <strong>fictional narratives</strong> created by
            artificial intelligence. They are not news reports or factual accounts of events.
          </p>
          <p>
            However, each story is grounded in real data gathered fresh each morning:
          </p>
          <ul className="list-disc pl-6 space-y-2 mt-3">
            <li>
              <strong>Weather</strong> — Current conditions and forecasts from the National Weather Service
            </li>
            <li>
              <strong>Tides</strong> — The rhythm of high and low water in the estuary
            </li>
            <li>
              <strong>Local News</strong> — Headlines from{' '}
              <a
                href="https://thelocalnews.news/category/ipswich/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sea-600 hover:text-sea-700 underline"
              >
                The Local News
              </a>
            </li>
            <li>
              <strong>Bird Sightings</strong> — Recent observations from{' '}
              <a
                href="https://ebird.org/region/US-MA-009"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sea-600 hover:text-sea-700 underline"
              >
                eBird
              </a>
              {' '}in Essex County
            </li>
            <li>
              <strong>River Conditions</strong> — Real-time flow data from the{' '}
              <a
                href="https://waterdata.usgs.gov/monitoring-location/01101500/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sea-600 hover:text-sea-700 underline"
              >
                USGS gauge
              </a>
              {' '}at the Ipswich River
            </li>
            <li>
              <strong>Season & Date</strong> — The time of year, its natural character, and astronomical events
            </li>
          </ul>
        </section>

        <section>
          <h3 className="text-lg font-semibold text-sea-700 mb-3">
            What the AI Creates
          </h3>
          <p>
            An AI model (Claude by Anthropic) weaves these ingredients into a short,
            contemplative narrative in the tradition of New England nature writing —
            think Thoreau observing Walden Pond, but for modern-day Ipswich.
          </p>
          <p>
            The AI has been given detailed knowledge of Ipswich's geography, history,
            wildlife, and seasonal rhythms to keep stories authentic to the place.
            But the prose itself — the observations, the connections drawn, the
            literary flourishes — are invented by the AI.
          </p>
        </section>

        <section>
          <h3 className="text-lg font-semibold text-sea-700 mb-3">
            Why I Made This
          </h3>
          <p>
            Ipswich Story Weaver is an experiment in using AI to create something
            gentle and grounded — a daily meditation on place rather than another
            feed of headlines.
          </p>
          <p>
            The national news can feel like noise — loud, fractured, designed to
            unsettle. Stories engineered to make us feel helpless and angry at
            people we'll never meet. I wanted to create something quieter, and I
            started by looking closer to home. Local news operates at human scale —
            neighbors helping neighbors, small decisions that shape our actual
            streets and schools. Here, those stories arrive embedded in place and
            season, held by land that has witnessed countless generations of
            concerns rise and fall like the tides. Not an escape from reality, but
            a gentler way of meeting it.
          </p>
        </section>

        <section className="bg-sand-50 border border-sand-200 rounded-lg p-4 mt-8">
          <h3 className="text-lg font-semibold text-sea-700 mb-3">
            Important Disclaimer
          </h3>
          <p className="text-sm">
            <strong>These stories are creative fiction.</strong> While they reference
            real news headlines, the narratives are AI-generated and should not be
            taken as factual reporting. Any resemblance to specific individuals or
            events beyond what appears in the source news is coincidental.
          </p>
        </section>

        <section className="text-sm text-gray-500 mt-8 pt-6 border-t border-sand-200">
          <p>
            <strong>Data Sources:</strong> Weather from National Weather Service,
            bird sightings from eBird (Cornell Lab of Ornithology), river flow from
            USGS Water Resources, news from The Local News RSS feed, tides from
            NOAA predictions.
          </p>
          <p className="mt-2">
            <strong>Technology:</strong> Stories generated by Claude (Anthropic).
            Built with FastAPI, React, and hosted on AWS.
          </p>
        </section>
      </div>
    </div>
  );
}
