import React, { useState } from 'react';
import { Card, CardHeader, CardContent, CardFooter, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';

const TopicRatingApp = () => {
  const topics = [
    'Technology',
    'Space',
    'AI',
    'Sustainability',
    'UNSDG',
    'Geopolitics',
    'Science',
    'Business',
    'Entrepreneurship'
  ];

  const [ratings, setRatings] = useState({});
  const [location, setLocation] = useState('');
  const [prompt, setPrompt] = useState('');

  const handleRatingChange = (topic, value) => {
    setRatings(prev => ({
      ...prev,
      [topic]: value[0]
    }));
  };

  const generatePrompt = () => {
    // Placeholder for prompt generation - to be customized later
    const promptData = {
      ratings,
      location,
      timestamp: new Date().toISOString()
    };
    setPrompt(JSON.stringify(promptData, null, 2));
  };

  const isValid = () => {
    return Object.keys(ratings).length === topics.length && 
           location.trim() !== '' &&
           Object.values(ratings).every(rating => rating >= 1 && rating <= 10);
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="text-2xl font-bold text-center">Topic Rating System</CardTitle>
      </CardHeader>
      
      <CardContent className="space-y-6">
        <div className="space-y-4">
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">Location Relevance</label>
            <Input
              type="text"
              placeholder="Enter location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full"
            />
          </div>

          {topics.map(topic => (
            <div key={topic} className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="text-sm font-medium">{topic}</label>
                <span className="text-sm font-mono">
                  {ratings[topic] || 1}
                </span>
              </div>
              <Slider
                defaultValue={[1]}
                max={10}
                min={1}
                step={1}
                value={[ratings[topic] || 1]}
                onValueChange={(value) => handleRatingChange(topic, value)}
                className="w-full"
              />
            </div>
          ))}
        </div>

        {prompt && (
          <div className="mt-4 p-4 bg-gray-100 rounded-lg">
            <pre className="whitespace-pre-wrap text-sm">{prompt}</pre>
          </div>
        )}
      </CardContent>

      <CardFooter>
        <Button 
          onClick={generatePrompt}
          disabled={!isValid()}
          className="w-full"
        >
          Generate Prompt
        </Button>
      </CardFooter>
    </Card>
  );
};

export default TopicRatingApp;