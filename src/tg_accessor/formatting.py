def split_news_into_chunks(news_list, max_len) -> list[str]:
    """Splits news into chunks of data digestable by a telegram bot."""

    chunks = []
    current_chunk = ''
    current_length = 0

    for news in news_list:
        news_text = f'{news.text} - [{news.url}]'
        news_length = len(news_text)

        if current_length + news_length > max_len:
            chunks.append(current_chunk.strip())
            current_chunk = ''
            current_length = 0

        current_chunk += news_text + '\n\n'
        current_length += news_length

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def format_telegram_message(chunks) -> list[str]:
    """Formats the chunks - if there's more then 1 page, adds pagination info."""

    result = []
    def prefix(i): return f'Part {i + 1} of {len(chunks)}:\n\n' if len(chunks) > 1 else ''
    for i, chunk in enumerate(chunks):
        formatted_text = ''
        formatted_text += prefix(i)
        formatted_text += chunk + '\n\n'
        result.append(formatted_text)

    return result
