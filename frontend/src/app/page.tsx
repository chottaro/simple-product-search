'use client';

import { useState } from 'react';

type ProductItem = {
  jan_code: string;
  product_name: {
    yahoo?: string;
    rakuten?: string;
    ebay?: string;
  };
  price: {
    yahoo: {
      min?: number;
      max?: number;
      target?: number;
    };
    rakuten: {
      min?: number;
      max?: number;
      target?: number;
    };
    ebay?: {
      min?: number;
      max?: number;
      target?: number;
    };
  };
  url: {
    yahoo?: string;
    rakuten?: string;
    ebay?: string;
  };
  image_url: {
    yahoo?: string;
    rakuten?: string;
    ebay?: string;
  };
};

export default function Home() {
  const [keyword, setKeyword] = useState('');
  const [results, setResults] = useState<ProductItem[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!keyword) return;

    setLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      const res = await fetch(`${apiUrl}/search?keyword=${encodeURIComponent(keyword)}`);
      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error('API call error:', err);
    }
    setLoading(false);
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Product search</h1>
      <div className="flex gap-2 mb-6">
        <input
          type="text"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="Enter keyword"
          className="border px-4 py-2 w-full"
        />
        <button
          onClick={handleSearch}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Search
        </button>
      </div>

      {loading && <p>Loading ...</p>}

      {results.length > 0 && (
        <ul className="space-y-4">
        {
          results.map((item, index) => (
            <div key={index} className="border p-4 rounded shadow">              
              <div className="text-lg font-semibold mb-1">
                {item.product_name?.yahoo ?? item.product_name?.rakuten ?? item.product_name?.ebay ?? 'No product name'}
              </div>

              <div className="mb-2">
                {item.price.yahoo?.min != null && item.price.yahoo?.max != null && (
                  item.price.yahoo.min === item.price.yahoo.max ? (
                    <div>yahoo: ¥{item.price.yahoo.min.toLocaleString('ja-JP')}</div>
                  ) : (
                    <div>yahoo: ¥{item.price.yahoo.min.toLocaleString('ja-JP')} ～ ¥{item.price.yahoo.max.toLocaleString('ja-JP')}</div>
                  )
                )}

                {item.price.rakuten?.min != null && item.price.rakuten?.max != null && (
                  item.price.rakuten.min === item.price.rakuten.max ? (
                    <div>rakuten: ¥{item.price.rakuten.min.toLocaleString('ja-JP')}</div>
                  ) : (
                    <div>rakuten: ¥{item.price.rakuten.min.toLocaleString('ja-JP')} ～ ¥{item.price.rakuten.max.toLocaleString('ja-JP')}</div>
                  )
                )}

                {item.price.ebay?.min != null && item.price.ebay?.max != null && (
                  item.price.ebay.min === item.price.ebay.max ? (
                    <div>eBay: ${item.price.ebay.min.toLocaleString('en-US')}</div>
                  ) : (
                    <div>eBay: ${item.price.ebay.min.toLocaleString('en-US')} ～ ${item.price.ebay.max.toLocaleString('en-US')}</div>
                  )
                )}
              </div>

              <div className="mb-2">
                {item.url.yahoo != null && (
                  <div>
                    ¥{item.price.yahoo.target.toLocaleString('ja-JP')}
                    <a href={String(item.url.yahoo)} target="_blank">
                      <img src={item.image_url?.yahoo} alt={item.product_name?.yahoo} width={100} className="rounded border" />
                    </a>
                  </div>
                )}
                <br />
                {item.url.rakuten != null && (
                  <div>
                    ¥{item.price.rakuten.target.toLocaleString('ja-JP')}
                    <a href={String(item.url.rakuten)} target="_blank">
                      <img src={item.image_url?.rakuten} alt={item.product_name?.rakuten} width={100} className="rounded border" />
                    </a>
                  </div>
                )}
                <br />
                {item.url.ebay != null && (
                  <div>
                    ${item.price.ebay.target.toLocaleString('en-US')}
                    <a href={String(item.url.ebay)} target="_blank">
                      <img src={item.image_url?.ebay} alt={item.product_name?.ebay} width={100} className="rounded border" />
                    </a>
                  </div>
                )}
              </div>
            </div>
          ))
        }
        </ul>
      )}
    </div>
  );
}
