export function normalizeBook(rawBook) {
  if (!rawBook) return null

  // fixture 형태: { pk, fields: {...} }
  if (rawBook.pk && rawBook.fields) {
    const fields = rawBook.fields
    return {
      id: rawBook.pk,
      title: fields.title ?? '',
      author: fields.author ?? '',
      cover: fields.cover ?? '',
      description: fields.description ?? '',
      isbn: fields.isbn ?? '',
      publisher: fields.publisher ?? '',
      pubDate: fields.pub_date ?? '',
      categoryId: fields.category ?? null,
      recommends: Array.isArray(fields.recommends) ? fields.recommends : [],
    }
  }

  // 일반 API 형태: { id, title, author, cover, ... }
  return {
    id: rawBook.id ?? rawBook.pk ?? null,
    title: rawBook.title ?? rawBook.name ?? '',
    author: rawBook.author ?? '',
    cover: rawBook.cover ?? rawBook.cover_url ?? '',
    description: rawBook.description ?? '',
    isbn: rawBook.isbn ?? '',
    publisher: rawBook.publisher ?? '',
    pubDate: rawBook.pub_date ?? rawBook.pubDate ?? '',
    categoryId: rawBook.category ?? rawBook.categoryId ?? null,
    recommends: Array.isArray(rawBook.recommends) ? rawBook.recommends : [],
  }
}

export function normalizeBookList(rawData) {
  const list = Array.isArray(rawData) ? rawData : (rawData?.results ?? [])
  return list.map(normalizeBook).filter(Boolean)
}
