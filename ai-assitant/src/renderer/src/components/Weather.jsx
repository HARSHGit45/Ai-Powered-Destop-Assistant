import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  WiDaySunny,
  WiCloudy,
  WiRain,
  WiSnow,
  WiThunderstorm,
  WiFog,
  WiHumidity,
  WiStrongWind
} from 'react-icons/wi';
import { FaSearch, FaTimes } from 'react-icons/fa';

const Weather = () => {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [location, setLocation] = useState('Pune');
  const [expanded, setExpanded] = useState(false);
  const synth = window.speechSynthesis;

  useEffect(() => {
    fetchWeatherData();
    const intervalId = setInterval(fetchWeatherData, 30 * 60 * 1000);
    return () => clearInterval(intervalId);
  }, [location]);

  useEffect(() => {
    if (expanded && weather) {
      readWeatherInfo();
    } else {
      synth.cancel();
    }
  }, [expanded, weather]);

  const fetchWeatherData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `https://api.openweathermap.org/data/2.5/weather?q=${location}&units=metric&appid=a86fc95313cea768e3e847e1a7147127`
      );

      if (!response.ok) {
        throw new Error('Weather data not available');
      }

      const data = await response.json();
      setWeather({
        location: data.name,
        temperature: Math.round(data.main.temp),
        condition: data.weather[0].main,
        description: data.weather[0].description,
        humidity: data.main.humidity,
        windSpeed: Math.round(data.wind.speed * 3.6)
      });
    } catch (err) {
      setError('Failed to fetch weather data.');
    } finally {
      setLoading(false);
    }
  };

  const readWeatherInfo = () => {
    if (synth.speaking) {
      synth.cancel();
    }

    const text = `Weather update for ${weather.location}. Temperature is ${weather.temperature} degrees Celsius. Condition: ${weather.condition}. Humidity is ${weather.humidity} percent, and wind speed is ${weather.windSpeed} kilometers per hour.`;

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    synth.speak(utterance);
  };

  const getWeatherIcon = (condition) => {
    switch (condition?.toLowerCase()) {
      case 'clear':
        return <WiDaySunny className="text-white" />;
      case 'clouds':
        return <WiCloudy className="text-gray-400" />;
      case 'rain':
      case 'drizzle':
        return <WiRain className="text-blue-400" />;
      case 'snow':
        return <WiSnow className="text-blue-200" />;
      case 'thunderstorm':
        return <WiThunderstorm className="text-purple-500" />;
      case 'mist':
      case 'fog':
      case 'haze':
        return <WiFog className="text-gray-300" />;
      default:
        return <WiDaySunny className="text-yellow-400" />;
    }
  };

  const handleLocationChange = (e) => {
    if (e.key === 'Enter') {
      setLocation(e.target.value);
    }
  };

  return (
    <div className="fixed top-6 left-6 z-50">
      {!expanded ? (
        <motion.div
          className="w-16 h-16 flex items-center justify-center bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700  backdrop-blur-md shadow-lg rounded-full cursor-pointer hover:scale-110 transition-all"
          animate={{ y: [0, -8, 0] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
          onClick={() => setExpanded(true)}
        >
          <div className="text-5xl">{getWeatherIcon(weather?.condition)}</div>
        </motion.div>
      ) : (
        <motion.div
          className="bg-white/20 backdrop-blur-lg shadow-xl rounded-2xl border border-gray-300 p-4 w-[550px] flex items-center justify-between space-x-4 hover:scale-105 transition-transform"
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -50 }}
        >
          {/* Weather Icon & Temperature */}
          <div className="flex items-center space-x-4">
            <motion.div
              className="text-6xl"
              animate={{ rotate: [0, 5, -5, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              {getWeatherIcon(weather?.condition)}
            </motion.div>
            <div>
              <h2 className="text-xl font-bold text-white">{weather?.location}</h2>
              <div className="text-5xl font-bold text-white">{weather?.temperature}°C</div>
              <div className="text-gray-200 capitalize">{weather?.description}</div>
            </div>
          </div>

          {/* Extra Weather Info */}
          <div className="flex flex-col text-white space-y-2">
            <div className="flex items-center">
              <WiHumidity className="text-blue-400 text-3xl" />
              <p className="text-sm ml-2">Humidity: {weather?.humidity}%</p>
            </div>
            <div className="flex items-center">
              <WiStrongWind className="text-gray-300 text-3xl" />
              <p className="text-sm ml-2">Wind: {weather?.windSpeed} km/h</p>
            </div>
          </div>

          {/* Close Button */}
          <div className="flex flex-col items-center gap-8">
            <FaTimes
              className="text-gray-300 cursor-pointer hover:text-red-500 ml-32"
              onClick={() => setExpanded(false)}
            />
            <div className="flex mt-4">
              <input
                type="text"
                className=" w-24 p-2 border border-gray-500 bg-transparent rounded-l text-white outline-none placeholder-gray-300"
                placeholder="Enter city"
                onKeyDown={handleLocationChange}
              />
              <button
                onClick={() => fetchWeatherData()}
                className="bg-blue-500 p-2 rounded-r text-white"
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

export default Weather;
