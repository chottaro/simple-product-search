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
          onKeyDown={(e) => {
            if (e.key === "Enter") handleSearch();
          }}
          placeholder="Enter keyword"
          className="border px-4 py-2 w-full"
          disabled={loading}
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className={`bg-blue-500 text-white px-4 py-2 rounded ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
        >
          Search
        </button>
      </div>

      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
          <div className="text-white text-xl">Loading ...</div>
        </div>
    )}

      {results.length > 0 && (
        <p className="mt-4 text-gray-700">{results.length} hits</p>
      )}

      {results.length > 0 && (
        <ul className="space-y-4">
        {
          results.map((item, index) => (
            <div key={index} className="border p-4 rounded shadow">
              <p className="font-bold mb-2">{item.product_name?.yahoo ?? item.product_name?.rakuten ?? item.product_name?.ebay ?? 'No product name'}</p>
              <div className="flex space-x-4">
                {['yahoo', 'rakuten', 'ebay'].map((store) => {
                  const url = item.url[store];
                  const imageUrl = item.image_url[store];
                  const price = item.price[store];
                  const min_price = price?.min;
                  const max_price = price?.max;

                  let currencySymbol = "";
                  let locale = "";

                  if (store === "ebay") {
                    currencySymbol = "$";
                    locale = "en-US";
                  } else {
                    currencySymbol = "¥";
                    locale = "ja-JP";
                  }

                  return (
                    <div key={store} className="w-full text-center">
                      <div className="mb-1 text-sm">
                        <span className="font-semibold capitalize">{store}</span>:{" "}
                        {min_price && max_price
                          ? `${currencySymbol}${min_price.toLocaleString(locale)} ～ ${currencySymbol}${max_price.toLocaleString(locale)}`
                          : "No Data."}
                      </div>
                      {url && imageUrl ? (
                        <a href={url} target="_blank" rel="noopener noreferrer">
                          <img
                            src={imageUrl}
                            alt={`${store} image`}
                            className="w-24 h-24 object-contain mx-auto border"
                          />
                        </a>
                      ) : (
                        <div className="w-24 h-24 flex items-center justify-center border mx-auto text-xs text-gray-400">
                          No Image
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))
        }
        </ul>
      )}
    </div>
  );
}
