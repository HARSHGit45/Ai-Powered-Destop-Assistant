import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FaChartLine, FaSearch, FaTimes } from 'react-icons/fa';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const API_KEY = '4d8cf4ce2511408c8b91a3903e14fb60' // Replace with your Twelve Data API Key

const Stocks = () => {
  const [stockData, setStockData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('Tesla');
  const [expanded, setExpanded] = useState(false);
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    fetchStockData();
    const intervalId = setInterval(fetchStockData, 30 * 60 * 1000);
    return () => clearInterval(intervalId);
  }, [searchQuery]);

  const fetchStockData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Search for the company to get the symbol
      const searchResponse = await fetch(
        `https://api.twelvedata.com/symbol_search?symbol=${searchQuery}&apikey=${API_KEY}`
      );
      const searchData = await searchResponse.json();

      if (!searchData.data || searchData.data.length === 0) {
        throw new Error('Company not found');
      }

      const symbol = searchData.data[0].symbol;

      // Fetch real-time stock data
      const response = await fetch(
        `https://api.twelvedata.com/time_series?symbol=${symbol}&interval=5min&apikey=${API_KEY}`
      );
      const data = await response.json();

      if (!data || !data.values) {
        throw new Error('Stock data not available');
      }

      const chartData = data.values.slice(0, 10).map((item) => ({
        time: item.datetime,
        price: parseFloat(item.open),
      }));

      setChartData(chartData.reverse());
      setStockData({
        symbol: symbol,
        company: searchData.data[0].instrument_name,
        price: parseFloat(data.values[0].open).toFixed(2),
      });
    } catch (err) {
      setError('Failed to fetch stock data.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed top-6 right-6 z-50">
      {!expanded ? (
        <motion.div
          className="w-16 h-16 flex items-center justify-center bg-white/20 backdrop-blur-md shadow-lg rounded-full cursor-pointer hover:scale-110 transition-all"
          animate={{ y: [0, -8, 0] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
          onClick={() => setExpanded(true)}
        >
          <div className="text-5xl text-green-400"><FaChartLine /></div>
        </motion.div>
      ) : (
        <motion.div
          className="bg-white/20 backdrop-blur-lg shadow-xl rounded-2xl border border-gray-300 p-4 w-[550px] flex flex-col items-center space-y-4 hover:scale-105 transition-transform"
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 50 }}
        >
          <div className="flex items-center space-x-4">
            <motion.div
              className="text-6xl text-green-400"
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <FaChartLine />
            </motion.div>
            <div>
              <h2 className="text-xl font-bold text-white">{stockData?.company}</h2>
              <h3 className="text-lg text-gray-300">({stockData?.symbol})</h3>
              <div className="text-5xl font-bold text-white">${stockData?.price}</div>
            </div>
          </div>
          
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData}>
              <XAxis dataKey="time" tick={{ fill: 'white', fontSize: 12 }} />
              <YAxis domain={['auto', 'auto']} tick={{ fill: 'white', fontSize: 12 }} />
              <Tooltip contentStyle={{ backgroundColor: 'black', color: 'white' }} />
              <Line type="monotone" dataKey="price" stroke="#00ff00" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
          
          <div className="flex items-center gap-4">
            <FaTimes
              className="text-gray-300 cursor-pointer hover:text-red-500"
              onClick={() => setExpanded(false)}
            />
            <div className="flex">
              <input
                type="text"
                className="w-32 p-2 border border-gray-500 bg-transparent rounded-l text-white outline-none placeholder-gray-300"
                placeholder="Enter company name"
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button
                onClick={() => fetchStockData()}
                className="bg-green-500 p-2 rounded-r text-white"
              >
                <FaSearch />
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default Stocks;
