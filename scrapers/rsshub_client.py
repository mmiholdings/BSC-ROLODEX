from api.app.modules.signal_engine import ingest_real_signals


if __name__ == '__main__':
    signals = ingest_real_signals()
    print(f'Fetched {len(signals)} real signals from RSSHub/HN')
    for s in signals[:10]:
        print('-', s.source, s.title[:90])
