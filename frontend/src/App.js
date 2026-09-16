import React, { useState, useEffect } from 'react';
import { 
  RefreshCw, 
  Search,
  TrendingDown,
  Minus,
  MessageSquare,
  PieChart,
  Tags,
  Cloud,
  Lightbulb,
  FileText,
  Smartphone,
  Apple,
  Moon,
  Sun,
  Star,
  BarChart3,
  Zap,
  TrendingUp as TrendIcon,
  Mail
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell,
  LineChart,
  Line,
  Legend
} from 'recharts';

// v1.0.1 - Build fix applied
// Mock data - replace with actual API calls
const mockData = {
  totalReviews: 6792,
  androidReviews: 5234,
  iosReviews: 1558,
  categorized: 590,
  pending: 6202,
  nps: 78,
  avgRating: 4.5,
  promoters: 0,
  passives: 0,
  detractors: 0,
  ratingDistribution: [
    { rating: 5, count: 799, percentage: 79.9 },
    { rating: 4, count: 82, percentage: 8.2 },
    { rating: 3, count: 22, percentage: 2.2 },
    { rating: 2, count: 10, percentage: 1.0 },
    { rating: 1, count: 87, percentage: 8.7 }
  ],
  sentimentSplit: {
    positive: 0,
    negative: 0,
    neutral: 0
  },
  themes: [
    { label: 'App Performance', count: 234, sentiment: 'negative' },
    { label: 'Customer Support', count: 189, sentiment: 'mixed' },
    { label: 'UI/UX Design', count: 156, sentiment: 'positive' },
    { label: 'Features Request', count: 134, sentiment: 'positive' },
    { label: 'Login Issues', count: 98, sentiment: 'negative' }
  ]
};

function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [activeTab, setActiveTab] = useState('reviews');
  const [platform, setPlatform] = useState('all');
  const [timePeriod, setTimePeriod] = useState('last30days');
  const [searchQuery, setSearchQuery] = useState('');
  const [sentimentFilter, setSentimentFilter] = useState('all');
  const [data, setData] = useState(mockData);
  const [loading, setLoading] = useState(false);
  const [lastSynced, setLastSynced] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [newReviewsCount, setNewReviewsCount] = useState(0);

  // Theme colors
  const colors = {
    primary: '#10b981', // emerald-500
    secondary: '#3b82f6', // blue-500
    warning: '#f59e0b', // amber-500
    danger: '#ef4444', // red-500
    background: darkMode ? '#0f172a' : '#f8fafc', // slate-900 : slate-50
    card: darkMode ? '#1e293b' : '#ffffff', // slate-800 : white
    text: darkMode ? '#f8fafc' : '#1e293b', // slate-50 : slate-800
    textMuted: darkMode ? '#94a3b8' : '#64748b', // slate-400 : slate-500
    border: darkMode ? '#334155' : '#e2e8f0' // slate-700 : slate-200
  };

  const fetchJsonWithFallback = async (urls) => {
    for (const u of urls) {
      try {
        const res = await fetch(u);
        if (res.ok) {
          return await res.json();
        }
      } catch (e) {
        // Try next fallback
      }
    }
    return null;
  };

  const fetchData = async (isManualSync = false) => {
    setLoading(true);
    try {
      const apiUrl = process.env.REACT_APP_API_URL || '';
      
      // Load reviews with fallbacks (local static / API / GitHub raw)
      const freshReviews = await fetchJsonWithFallback([
        '/data/privacy_safe_reviews.json',
        `${apiUrl}/api/reviews`,
        'https://raw.githubusercontent.com/pbehuray/m3-weeklyPulseReport/master/phase4/data/privacy_safe/privacy_safe_reviews.json'
      ]) || [];

      if (freshReviews.length > 0) {
        setReviews(freshReviews);
        const previousCount = reviews.length;
        const newCount = freshReviews.length - previousCount;
        if (newCount > 0) {
          setNewReviewsCount(newCount);
        }
      }

      // Load weekly pulse with fallbacks
      const pulseData = await fetchJsonWithFallback([
        '/data/weekly_pulse.json',
        `${apiUrl}/api/pulse`,
        'https://raw.githubusercontent.com/pbehuray/m3-weeklyPulseReport/master/phase8/data/weekly_pulse/weekly_pulse.json'
      ]) || {};

      // Load docs delivery status
      const docsData = await fetchJsonWithFallback([
        '/data/phase9_delivery_status.json',
        `${apiUrl}/api/docs-status`,
        'https://raw.githubusercontent.com/pbehuray/m3-weeklyPulseReport/master/phase9/data/docs_delivery/phase9_delivery_status.json'
      ]) || {};

      // Load gmail delivery status
      const gmailData = await fetchJsonWithFallback([
        '/data/phase10_gmail_status.json',
        `${apiUrl}/api/gmail-status`,
        'https://raw.githubusercontent.com/pbehuray/m3-weeklyPulseReport/master/phase10/data/gmail_delivery/phase10_gmail_status.json'
      ]) || {};

      const now = new Date();
      now.setHours(23, 59, 59, 999);

      const filteredByDate = freshReviews.filter(r => {
        if (!r.date) return false;
        const reviewDate = new Date(r.date);
        const daysDiff = (now - reviewDate) / (1000 * 60 * 60 * 24);
        
        switch(timePeriod) {
          case 'today':
            return daysDiff <= 1;
          case 'yesterday':
            return daysDiff > 1 && daysDiff <= 2;
          case 'last7days':
            return daysDiff <= 7;
          case 'last15days':
            return daysDiff <= 15;
          case 'last30days':
          default:
            return daysDiff <= 30;
        }
      });
      
      // If timePeriod filter yields empty (e.g. historical data window), use full review set
      const reviewsToUse = filteredByDate.length > 0 ? filteredByDate : freshReviews;
      
      const totalReviews = reviewsToUse.length;
      const androidReviews = reviewsToUse.filter(r => r.platform === 'android' || r.platform === 'play_store' || r.source === 'play_store').length;
      const iosReviews = reviewsToUse.filter(r => r.platform === 'ios' || r.platform === 'app_store' || r.source === 'app_store').length;
      
      const ratingCounts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0};
      reviewsToUse.forEach(r => {
        const rating = Math.round(r.score || r.rating || 0);
        if (rating >= 1 && rating <= 5) {
          ratingCounts[rating]++;
        }
      });
      
      const totalWithRating = reviewsToUse.length || 1;
      const ratingDistribution = [
        { rating: 5, count: ratingCounts[5], percentage: ((ratingCounts[5] / totalWithRating) * 100).toFixed(1) },
        { rating: 4, count: ratingCounts[4], percentage: ((ratingCounts[4] / totalWithRating) * 100).toFixed(1) },
        { rating: 3, count: ratingCounts[3], percentage: ((ratingCounts[3] / totalWithRating) * 100).toFixed(1) },
        { rating: 2, count: ratingCounts[2], percentage: ((ratingCounts[2] / totalWithRating) * 100).toFixed(1) },
        { rating: 1, count: ratingCounts[1], percentage: ((ratingCounts[1] / totalWithRating) * 100).toFixed(1) }
      ];
      
      const sentimentCounts = { positive: 0, negative: 0, neutral: 0 };
      reviewsToUse.forEach(r => {
        const sentiment = (r.sentiment || r.rating_label || '').toLowerCase();
        if (sentiment.includes('positive')) sentimentCounts.positive++;
        else if (sentiment.includes('negative')) sentimentCounts.negative++;
        else sentimentCounts.neutral++;
      });
      
      const totalWithSentiment = reviewsToUse.length || 1;
      const sentimentSplit = {
        positive: Math.round((sentimentCounts.positive / totalWithSentiment) * 100),
        negative: Math.round((sentimentCounts.negative / totalWithSentiment) * 100),
        neutral: Math.round((sentimentCounts.neutral / totalWithSentiment) * 100)
      };
      
      const totalRatingSum = reviewsToUse.reduce((sum, r) => sum + (r.rating || r.score || 0), 0);
      const avgRating = reviewsToUse.length > 0 ? (totalRatingSum / reviewsToUse.length).toFixed(1) : "4.3";
      
      const transformedData = {
        totalReviews,
        androidReviews,
        iosReviews,
        categorized: (pulseData.top_themes?.length || 3) * 50,
        pending: Math.max(0, totalReviews - 500),
        nps: pulseData.nps || 72,
        avgRating: parseFloat(avgRating),
        promoters: ratingCounts[5] + ratingCounts[4],
        passives: ratingCounts[3],
        detractors: ratingCounts[1] + ratingCounts[2],
        ratingDistribution,
        sentimentSplit,
        themes: pulseData.top_themes?.map((theme, idx) => ({
          label: theme.label || theme.theme_name || `Theme ${idx + 1}`,
          description: theme.description || theme.summary || `Users frequently discuss ${theme.label || theme.theme_name}`,
          count: theme.review_count || [234, 189, 156, 134, 98][idx] || 100,
          sentiment: theme.sentiment || ['negative', 'mixed', 'positive', 'positive', 'negative'][idx] || 'mixed'
        })) || mockData.themes,
        headline: pulseData.headline || mockData.headline,
        quotes: pulseData.quotes || [
          "Support never responds when withdrawals fail for days.",
          "App crashes during trading sessions on market open.",
          "They cut more charges than what they said on a sell."
        ],
        actions: pulseData.actions || [
          "Audit unresolved support journeys and create a weekly queue for high-frequency review complaints.",
          "Review the most common feedback examples and convert recurring friction into a product improvement backlog item.",
          "Prioritize crash and latency diagnostics for the most recent app versions mentioned in reviews."
        ],
        docsUrl: docsData.document_url || 'https://docs.google.com/document/d/1IsqpOHq53G51Shg5R271iq7P57k6wUqqQKVNzJVA6dw/edit',
        recipient: gmailData.recipient || 'support-team@groww.in',
      };
      
      setData(transformedData);
      setLastSynced(new Date());
      
      if (isManualSync) {
        alert(`Synced ${freshReviews.length} reviews successfully!`);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      setData(mockData);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(false); // Auto-fetch without alert
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [platform, timePeriod]);

  const navItems = [
    { id: 'reviews', label: 'Reviews', icon: MessageSquare },
    { id: 'analytics', label: 'Analytics', icon: PieChart },
    { id: 'categories', label: 'Categories', icon: Tags },
    { id: 'wordcloud', label: 'Word Cloud', icon: Cloud },
    { id: 'ideation', label: 'Ideation', icon: Lightbulb },
    { id: 'reporting', label: 'Reporting', icon: FileText }
  ];


  const getRatingColor = (rating) => {
    switch(rating) {
      case 5: return '#10b981';
      case 4: return '#34d399';
      case 3: return '#f59e0b';
      case 2: return '#f97316';
      case 1: return '#ef4444';
      default: return '#6b7280';
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: colors.background,
      color: colors.text,
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      {/* Header */}
      <header style={{ 
        backgroundColor: colors.card, 
        borderBottom: `1px solid ${colors.border}`,
        padding: '16px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ 
            width: '40px', 
            height: '40px', 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 'bold',
            fontSize: '20px'
          }}>
            G
          </div>
          <div>
            <h1 style={{ margin: 0, fontSize: '20px', fontWeight: '600' }}>Support PM Pulsator</h1>
            <p style={{ margin: 0, fontSize: '13px', color: colors.textMuted }}>AI-Powered Review Intelligence</p>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={() => setDarkMode(!darkMode)}
            style={{
              padding: '8px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: colors.border,
              color: colors.text,
              cursor: 'pointer'
            }}
          >
            {darkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>
          
          <div style={{ display: 'flex', gap: '8px' }}>
            <button 
              onClick={() => setPlatform('all')}
              style={{
                padding: '8px 16px',
                borderRadius: '20px',
                border: 'none',
                backgroundColor: platform === 'all' ? '#10b981' : colors.border,
                color: platform === 'all' ? 'white' : colors.text,
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: '500'
              }}
            >
              All
            </button>
            <button 
              onClick={() => setPlatform('android')}
              style={{
                padding: '8px 16px',
                borderRadius: '20px',
                border: 'none',
                backgroundColor: platform === 'android' ? '#10b981' : colors.border,
                color: platform === 'android' ? 'white' : colors.text,
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <Smartphone size={14} /> Android
            </button>
            <button 
              onClick={() => setPlatform('ios')}
              style={{
                padding: '8px 16px',
                borderRadius: '20px',
                border: 'none',
                backgroundColor: platform === 'ios' ? '#10b981' : colors.border,
                color: platform === 'ios' ? 'white' : colors.text,
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <Apple size={14} /> iOS
            </button>
          </div>

          <button
            onClick={() => fetchData(true)}
            disabled={loading}
            style={{
              padding: '8px 16px',
              borderRadius: '8px',
              border: `1px solid ${colors.border}`,
              backgroundColor: 'transparent',
              color: colors.text,
              cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '13px'
            }}
          >
            <RefreshCw size={16} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
            Sync {platform === 'android' ? 'Android' : platform === 'ios' ? 'iOS' : 'All'}
          </button>
        </div>
      </header>

      {/* Navigation */}
      <nav style={{ 
        backgroundColor: colors.card, 
        borderBottom: `1px solid ${colors.border}`,
        padding: '0 24px'
      }}>
        <div style={{ display: 'flex', gap: '8px' }}>
          {navItems.map(item => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                style={{
                  padding: '12px 20px',
                  border: 'none',
                  backgroundColor: 'transparent',
                  color: activeTab === item.id ? '#10b981' : colors.textMuted,
                  borderBottom: `2px solid ${activeTab === item.id ? '#10b981' : 'transparent'}`,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '14px',
                  fontWeight: '500'
                }}
              >
                <Icon size={18} />
                {item.label}
              </button>
            );
          })}
        </div>
      </nav>

      {/* Main Content */}
      <main style={{ padding: '24px' }}>
        {activeTab === 'reviews' && (
          <>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
              <div>
                <h2 style={{ margin: '0 0 4px 0', fontSize: '20px', fontWeight: '600' }}>Reviews</h2>
                <p style={{ margin: 0, color: colors.textMuted, fontSize: '14px' }}>Triage and analyze Groww app store reviews</p>
              </div>
              <button
                style={{
                  padding: '8px 16px',
                  borderRadius: '8px',
                  border: `1px solid ${colors.border}`,
                  backgroundColor: 'transparent',
                  color: colors.text,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '13px'
                }}
              >
                <RefreshCw size={14} />
                Import CSV
              </button>
            </div>

            {/* Reviews Summary Card */}
            <div style={{ 
              backgroundColor: colors.card,
              borderRadius: '12px',
              padding: '16px 20px',
              marginBottom: '16px',
              border: `1px solid ${colors.border}`,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <MessageSquare size={18} style={{ color: '#10b981' }} />
                <span style={{ fontSize: '16px', fontWeight: '600' }}>
                  6,792 reviews
                </span>
                <span style={{ color: '#10b981', fontSize: '13px' }}>
                  ● Android: 8h ago
                </span>
                <span style={{ color: '#10b981', fontSize: '13px' }}>
                  ● iOS: 8h ago
                </span>
              </div>
              <button
                style={{
                  padding: '6px 12px',
                  borderRadius: '6px',
                  border: 'none',
                  backgroundColor: 'transparent',
                  color: colors.textMuted,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '13px'
                }}
              >
                <RefreshCw size={14} />
                Refresh
              </button>
            </div>

            {/* AI Categorization */}
            <div style={{ 
              backgroundColor: darkMode ? '#1e293b' : '#f1f5f9',
              borderRadius: '12px',
              padding: '16px 20px',
              marginBottom: '16px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ 
                  width: '32px', 
                  height: '32px', 
                  backgroundColor: '#8b5cf6',
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <PieChart size={18} color="white" />
                </div>
                <div>
                  <p style={{ margin: 0, fontSize: '14px', fontWeight: '600' }}>AI Categorization</p>
                  <p style={{ margin: '2px 0 0 0', fontSize: '12px', color: colors.textMuted }}>
                    590 of 6792 categorized • <span style={{ color: '#f59e0b' }}>6202 pending</span>
                  </p>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ 
                  width: '120px', 
                  height: '6px', 
                  backgroundColor: colors.border,
                  borderRadius: '3px',
                  overflow: 'hidden'
                }}>
                  <div style={{ 
                    width: '9%',
                    height: '100%',
                    backgroundColor: '#10b981',
                    borderRadius: '3px'
                  }} />
                </div>
                <span style={{ fontSize: '12px', color: colors.textMuted }}>9%</span>
                <button
                  style={{
                    padding: '8px 16px',
                    borderRadius: '6px',
                    border: 'none',
                    backgroundColor: '#8b5cf6',
                    color: 'white',
                    cursor: 'pointer',
                    fontSize: '13px',
                    fontWeight: '500'
                  }}
                >
                  Categorize
                </button>
              </div>
            </div>

            {/* Platform & Time Filters */}
            <div style={{ 
              backgroundColor: colors.card,
              borderRadius: '12px',
              padding: '16px 20px',
              marginBottom: '24px',
              border: `1px solid ${colors.border}`
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', gap: '40px' }}>
                  <div>
                    <p style={{ margin: '0 0 8px 0', fontSize: '11px', textTransform: 'uppercase', color: colors.textMuted, fontWeight: '600', letterSpacing: '0.5px' }}>Platform</p>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      {['All', 'Android', 'iOS'].map(p => (
                        <button
                          key={p}
                          onClick={() => setPlatform(p.toLowerCase())}
                          style={{
                            padding: '6px 14px',
                            borderRadius: '20px',
                            border: 'none',
                            backgroundColor: (p === 'All' ? platform === 'all' : platform === p.toLowerCase()) ? '#10b981' : colors.border,
                            color: (p === 'All' ? platform === 'all' : platform === p.toLowerCase()) ? 'white' : colors.text,
                            cursor: 'pointer',
                            fontSize: '13px'
                          }}
                        >
                          {p}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p style={{ margin: '0 0 8px 0', fontSize: '11px', textTransform: 'uppercase', color: colors.textMuted, fontWeight: '600', letterSpacing: '0.5px' }}>Time Period</p>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      {['Today', 'Yesterday', 'Last 7 Days', 'Last 15 Days', 'Last 30 Days'].map(period => (
                        <button
                          key={period}
                          onClick={() => setTimePeriod(period.toLowerCase().replace(/\s/g, ''))}
                          style={{
                            padding: '6px 14px',
                            borderRadius: '20px',
                            border: 'none',
                            backgroundColor: timePeriod === period.toLowerCase().replace(/\s/g, '') ? '#10b981' : colors.border,
                            color: timePeriod === period.toLowerCase().replace(/\s/g, '') ? 'white' : colors.text,
                            cursor: 'pointer',
                            fontSize: '13px'
                          }}
                        >
                          {period}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
                <button 
                  onClick={() => {setPlatform('all'); setTimePeriod('last30days');}}
                  style={{ color: colors.textMuted, fontSize: '13px', background: 'none', border: 'none', cursor: 'pointer' }}
                >
                  Reset
                </button>
              </div>
            </div>

            {/* Rating Distribution & Health Metrics */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
              {/* Rating Distribution */}
              <div style={{ 
                backgroundColor: colors.card,
                borderRadius: '12px',
                padding: '20px',
                border: `1px solid ${colors.border}`
              }}>
                <h3 style={{ margin: '0 0 20px 0', fontSize: '13px', fontWeight: '600', color: colors.textMuted, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Rating Distribution</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {(data.ratingDistribution || [
                    { rating: 5, count: 0, percentage: 0 },
                    { rating: 4, count: 0, percentage: 0 },
                    { rating: 3, count: 0, percentage: 0 },
                    { rating: 2, count: 0, percentage: 0 },
                    { rating: 1, count: 0, percentage: 0 }
                  ]).map((item) => (
                    <div key={item.rating} style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ color: getRatingColor(item.rating), fontSize: '13px', minWidth: '20px', fontWeight: 600 }}>{item.rating}★</span>
                      <div style={{ flex: 1, height: '10px', backgroundColor: darkMode ? '#1e293b' : '#e2e8f0', borderRadius: '5px', overflow: 'hidden' }}>
                        <div style={{ width: `${item.percentage}%`, height: '100%', backgroundColor: getRatingColor(item.rating), borderRadius: '5px' }} />
                      </div>
                      <span style={{ fontSize: '13px', color: colors.text, minWidth: '28px', textAlign: 'right' }}>{item.count}</span>
                      <span style={{ fontSize: '12px', color: colors.textMuted, minWidth: '36px', textAlign: 'right' }}>{item.percentage}%</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Health Metrics */}
              <div style={{ 
                backgroundColor: colors.card,
                borderRadius: '12px',
                padding: '20px',
                border: `1px solid ${colors.border}`
              }}>
                <h3 style={{ margin: '0 0 20px 0', fontSize: '13px', fontWeight: '600', color: colors.textMuted, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Health Metrics</h3>
                
                {/* NPS Card */}
                <div style={{ backgroundColor: darkMode ? '#064e3b' : '#f0fdf4', borderRadius: '10px', padding: '16px', marginBottom: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <p style={{ margin: '0 0 4px 0', fontSize: '11px', color: colors.textMuted, textTransform: 'uppercase' }}>NPS</p>
                      <p style={{ margin: 0, fontSize: '28px', fontWeight: '700', color: '#10b981' }}>+{data.nps || 0}</p>
                      <p style={{ margin: '4px 0 0 0', fontSize: '12px', color: '#10b981' }}>{(data.nps || 0) >= 50 ? 'Excellent' : (data.nps || 0) >= 30 ? 'Good' : (data.nps || 0) >= 0 ? 'Average' : 'Poor'}</p>
                    </div>
                    <div style={{ textAlign: 'right', fontSize: '11px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px', justifyContent: 'flex-end' }}>
                        <span style={{ color: '#10b981' }}>●</span>
                        <span style={{ color: colors.textMuted }}>Promoters (4-5):</span>
                        <span style={{ color: colors.text }}>{data.promoters || 0}</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '3px', justifyContent: 'flex-end' }}>
                        <span style={{ color: '#f59e0b' }}>●</span>
                        <span style={{ color: colors.textMuted }}>Passives (3):</span>
                        <span style={{ color: colors.text }}>{data.passives || 0}</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', justifyContent: 'flex-end' }}>
                        <span style={{ color: '#ef4444' }}>●</span>
                        <span style={{ color: colors.textMuted }}>Detractors (1-2):</span>
                        <span style={{ color: colors.text }}>{data.detractors || 0}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Stats Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                  <div style={{ backgroundColor: darkMode ? '#1e293b' : '#f8fafc', borderRadius: '8px', padding: '14px' }}>
                    <p style={{ margin: '0 0 4px 0', fontSize: '10px', color: colors.textMuted, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Total Reviews</p>
                    <p style={{ margin: 0, fontSize: '20px', fontWeight: '700' }}>{data.totalReviews?.toLocaleString() || 0}</p>
                  </div>
                  <div style={{ backgroundColor: darkMode ? '#1e293b' : '#f8fafc', borderRadius: '8px', padding: '14px' }}>
                    <p style={{ margin: '0 0 4px 0', fontSize: '10px', color: colors.textMuted, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Avg Rating</p>
                    <p style={{ margin: 0, fontSize: '20px', fontWeight: '700' }}>{data.avgRating || 0}<span style={{ color: '#f59e0b', marginLeft: '4px' }}>★</span></p>
                  </div>
                </div>

                {/* Sentiment Split */}
                <div>
                  <p style={{ margin: '0 0 10px 0', fontSize: '10px', color: colors.textMuted, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Sentiment Split</p>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <div style={{ flex: 1, textAlign: 'center', padding: '10px', backgroundColor: darkMode ? '#1e293b' : '#f0fdf4', borderRadius: '6px' }}>
                      <TrendIcon size={14} style={{ color: '#10b981', marginBottom: '4px' }} />
                      <p style={{ margin: 0, fontSize: '12px', color: colors.textMuted }}>{data.sentimentSplit?.positive || 0}%</p>
                    </div>
                    <div style={{ flex: 1, textAlign: 'center', padding: '10px', backgroundColor: darkMode ? '#1e293b' : '#fefce8', borderRadius: '6px' }}>
                      <Minus size={14} style={{ color: '#eab308', marginBottom: '4px' }} />
                      <p style={{ margin: 0, fontSize: '12px', color: colors.textMuted }}>{data.sentimentSplit?.neutral || 0}%</p>
                    </div>
                    <div style={{ flex: 1, textAlign: 'center', padding: '10px', backgroundColor: darkMode ? '#1e293b' : '#fef2f2', borderRadius: '6px' }}>
                      <TrendingDown size={14} style={{ color: '#ef4444', marginBottom: '4px' }} />
                      <p style={{ margin: 0, fontSize: '12px', color: colors.textMuted }}>{data.sentimentSplit?.negative || 0}%</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Search & Filter */}
            <div style={{ 
              backgroundColor: colors.card,
              borderRadius: '12px',
              padding: '16px',
              marginBottom: '24px',
              border: `1px solid ${colors.border}`,
              display: 'flex',
              gap: '16px',
              alignItems: 'center'
            }}>
              <div style={{ flex: 1, position: 'relative' }}>
                <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: colors.textMuted }} />
                <input
                  type="text"
                  placeholder="Search reviews..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 12px 10px 40px',
                    borderRadius: '8px',
                    border: `1px solid ${colors.border}`,
                    backgroundColor: darkMode ? '#0f172a' : '#f8fafc',
                    color: colors.text,
                    fontSize: '14px',
                    outline: 'none'
                  }}
                />
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '12px', color: colors.textMuted }}>SENTIMENT</span>
                {['all', 'positive', 'negative', 'neutral'].map(s => (
                  <button
                    key={s}
                    onClick={() => setSentimentFilter(s)}
                    style={{
                      padding: '8px 16px',
                      borderRadius: '20px',
                      border: 'none',
                      backgroundColor: sentimentFilter === s ? '#10b981' : colors.border,
                      color: sentimentFilter === s ? 'white' : colors.text,
                      cursor: 'pointer',
                      fontSize: '13px',
                      textTransform: 'capitalize'
                    }}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            {/* Individual Review Cards */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {reviews.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '40px', color: colors.textMuted }}>
                  <p>No reviews loaded. Click "Sync Reviews" to fetch data.</p>
                </div>
              ) : reviews.filter(review => {
                // Apply search filter
                if (searchQuery) {
                  const text = (review.review_text || review.content || '').toLowerCase();
                  if (!text.includes(searchQuery.toLowerCase())) return false;
                }
                // Apply sentiment filter
                if (sentimentFilter === 'all') return true;
                const sentiment = (review.rating_label || '').toLowerCase();
                if (sentimentFilter === 'positive') return sentiment.includes('positive');
                if (sentimentFilter === 'negative') return sentiment.includes('negative');
                if (sentimentFilter === 'neutral') return !sentiment.includes('positive') && !sentiment.includes('negative');
                return true;
              }).slice(0, 10).map((review, idx) => (
                <div 
                  key={idx}
                  style={{
                    backgroundColor: colors.card,
                    borderRadius: '12px',
                    padding: '20px',
                    border: `1px solid ${colors.border}`
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div style={{ 
                        width: '40px', 
                        height: '40px', 
                        backgroundColor: colors.border,
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <span style={{ fontSize: '16px', fontWeight: '600', color: colors.text }}>{(review.reviewer_name || review.userName || 'User').charAt(0).toUpperCase()}</span>
                      </div>
                      <div>
                        <p style={{ margin: 0, fontWeight: '600', fontSize: '14px' }}>{review.reviewer_name || review.userName || 'Anonymous'}</p>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '2px' }}>
                          <span style={{ fontSize: '12px', color: colors.textMuted }}>{review.platform || review.source || 'Unknown'}</span>
                          <span style={{ fontSize: '12px', color: colors.textMuted }}>•</span>
                          <span style={{ fontSize: '12px', color: colors.textMuted }}>{review.review_date || review.date || 'Recent'}</span>
                        </div>
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div style={{ display: 'flex', gap: '2px' }}>
                        {[...Array(5)].map((_, i) => (
                          <Star key={i} size={14} fill={i < (review.score || review.rating || 0) ? '#f59e0b' : 'transparent'} color={i < (review.score || review.rating || 0) ? '#f59e0b' : colors.border} />
                        ))}
                      </div>
                      <span style={{ 
                        padding: '4px 12px', 
                        borderRadius: '12px', 
                        backgroundColor: (review.rating_label || '').toLowerCase().includes('positive') ? '#d4edda' : (review.rating_label || '').toLowerCase().includes('negative') ? '#f8d7da' : '#fff3cd',
                        color: (review.rating_label || '').toLowerCase().includes('positive') ? '#155724' : (review.rating_label || '').toLowerCase().includes('negative') ? '#721c24' : '#856404',
                        fontSize: '12px',
                        fontWeight: '500',
                        textTransform: 'capitalize'
                      }}>
                        {review.rating_label || 'Neutral'}
                      </span>
                    </div>
                  </div>
                  <p style={{ margin: '0 0 16px 0', fontSize: '15px', color: colors.text, lineHeight: 1.5 }}>
                    {review.content || review.text || review.review_text || 'No content'}
                  </p>
                  <div style={{ display: 'flex', gap: '16px' }}>
                    <button style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: colors.textMuted, background: 'none', border: 'none', cursor: 'pointer' }}>
                      <MessageSquare size={14} />
                      Reply
                    </button>
                    <button style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: colors.textMuted, background: 'none', border: 'none', cursor: 'pointer' }}>
                      <Search size={14} />
                      Find Similar
                    </button>
                  </div>
                </div>
              )).concat(
                (() => {
                  const filtered = reviews.filter(review => {
                    if (sentimentFilter === 'all') return true;
                    const sentiment = (review.rating_label || '').toLowerCase();
                    if (sentimentFilter === 'positive') return sentiment.includes('positive');
                    if (sentimentFilter === 'negative') return sentiment.includes('negative');
                    if (sentimentFilter === 'neutral') return !sentiment.includes('positive') && !sentiment.includes('negative');
                    return true;
                  });
                  if (filtered.length === 0) {
                    return [<div key="empty" style={{ textAlign: 'center', padding: '40px', color: colors.textMuted }}><p>No {sentimentFilter} reviews found.</p></div>];
                  }
                  if (filtered.length > 10) {
                    return [<div key="more" style={{ textAlign: 'center', padding: '20px', color: colors.textMuted }}><p>Showing first 10 of {filtered.length} {sentimentFilter} reviews. {reviews.length} total in dataset.</p></div>];
                  }
                  return [];
                })()
              )}
            </div>
          </>
        )}

        {activeTab === 'analytics' && (
          <>
            {/* Analytics Header */}
            <div style={{ marginBottom: '24px' }}>
              <h2 style={{ margin: '0 0 8px 0', fontSize: '24px', fontWeight: '600' }}>Analytics</h2>
              <p style={{ margin: 0, color: colors.textMuted }}>Grow app metrics, sentiment analysis, and trend insights</p>
            </div>

            {/* Filters */}
            <div style={{ 
              backgroundColor: colors.card,
              borderRadius: '12px',
              padding: '20px',
              marginBottom: '24px',
              border: `1px solid ${colors.border}`
            }}>
              <div style={{ display: 'flex', gap: '40px' }}>
                <div>
                  <p style={{ margin: '0 0 12px 0', fontSize: '12px', textTransform: 'uppercase', color: colors.textMuted, fontWeight: '600' }}>Platform</p>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    {['all', 'android', 'ios'].map(p => (
                      <button
                        key={p}
                        onClick={() => setPlatform(p)}
                        style={{
                          padding: '8px 16px',
                          borderRadius: '20px',
                          border: 'none',
                          backgroundColor: platform === p ? '#10b981' : colors.border,
                          color: platform === p ? 'white' : colors.text,
                          cursor: 'pointer',
                          fontSize: '13px',
                          textTransform: 'capitalize'
                        }}
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <p style={{ margin: '0 0 12px 0', fontSize: '12px', textTransform: 'uppercase', color: colors.textMuted, fontWeight: '600' }}>Time Period</p>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    {['Today', 'Yesterday', 'Last 7 Days', 'Last 15 Days', 'Last 30 Days'].map(period => (
                      <button
                        key={period}
                        onClick={() => setTimePeriod(period.toLowerCase().replace(/\s/g, ''))}
                        style={{
                          padding: '8px 16px',
                          borderRadius: '20px',
                          border: 'none',
                          backgroundColor: timePeriod === period.toLowerCase().replace(/\s/g, '') ? '#10b981' : colors.border,
                          color: timePeriod === period.toLowerCase().replace(/\s/g, '') ? 'white' : colors.text,
                          cursor: 'pointer',
                          fontSize: '13px'
                        }}
                      >
                        {period}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
              <button 
                onClick={() => {setPlatform('all'); setTimePeriod('last30days');}}
                style={{ color: colors.textMuted, fontSize: '13px', background: 'none', border: 'none', cursor: 'pointer' }}
              >
                Reset
              </button>
            </div>

            {/* Metrics Grid */}
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(5, 1fr)', 
              gap: '16px',
              marginBottom: '24px'
            }}>
              <div style={{ 
                backgroundColor: colors.card,
                borderRadius: '12px',
                padding: '20px',
                border: `1px solid ${colors.border}`
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <MessageSquare size={16} color={colors.textMuted} />
                  <span style={{ fontSize: '12px', color: colors.textMuted, textTransform: 'uppercase' }}>Total Reviews</span>
                </div>
                <p style={{ margin: 0, fontSize: '28px', fontWeight: '700' }}>{data.totalReviews?.toLocaleString() || 0}</p>
              </div>

              <div style={{ 
                backgroundColor: colors.card,
                borderRadius: '12px',
                padding: '20px',
                border: `1px solid ${colors.border}`
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <Star size={16} color="#f59e0b" />
                  <span style={{ fontSize: '12px', color: colors.textMuted, textTransform: 'uppercase' }}>Avg Rating</span>
                </div>
                <p style={{ margin: 0, fontSize: '28px', fontWeight: '700' }}>{data.avgRating || 0}</p>
                <p style={{ margin: '4px 0 0 0', fontSize: '12px', color: colors.textMuted }}>out of 5.0</p>
              </div>

              <div style={{ 
                backgroundColor: colors.card,
                borderRadius: '12px',
                padding: '20px',
                border: `1px solid ${colors.border}`
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <TrendIcon size={16} color="#10b981" />
                  <span style={{ fontSize: '12px', color: colors.textMuted, textTransform: 'uppercase' }}>Positive</span>
                </div>
                <p style={{ margin: 0, fontSize: '28px', fontWeight: '700', color: '#10b981' }}>{data.sentimentSplit?.positive || 0}%</p>
              </div>

              <div style={{ 
                backgroundColor: colors.card,
                borderRadius: '12px',
                padding: '20px',
                border: `1px solid ${colors.border}`
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <TrendingDown size={16} color="#ef4444" />
                  <span style={{ fontSize: '12px', color: colors.textMuted, textTransform: 'uppercase' }}>Negative</span>
                </div>
                <p style={{ margin: 0, fontSize: '28px', fontWeight: '700', color: '#ef4444' }}>{data.sentimentSplit?.negative || 0}%</p>
              </div>

              <div style={{ 
                backgroundColor: colors.card,
                borderRadius: '12px',
                padding: '20px',
                border: `1px solid ${colors.border}`
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <Minus size={16} color="#eab308" />
                  <span style={{ fontSize: '12px', color: colors.textMuted, textTransform: 'uppercase' }}>Neutral</span>
                </div>
                <p style={{ margin: 0, fontSize: '28px', fontWeight: '700', color: '#eab308' }}>{data.sentimentSplit?.neutral || 0}%</p>
              </div>
            </div>

            {/* Charts Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
              {/* Sentiment Analysis */}
              <div style={{ 
                backgroundColor: colors.card,
                borderRadius: '12px',
                padding: '24px',
                border: `1px solid ${colors.border}`
              }}>
                <h3 style={{ margin: '0 0 20px 0', fontSize: '16px', fontWeight: '600' }}>Sentiment Analysis</h3>
                <div style={{ height: '250px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={[
                      { name: 'Positive', value: data.sentimentSplit?.positive || 0, color: '#10b981' },
                      { name: 'Neutral', value: data.sentimentSplit?.neutral || 0, color: '#f59e0b' },
                      { name: 'Negative', value: data.sentimentSplit?.negative || 0, color: '#ef4444' }
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" stroke={colors.border} vertical={false} />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: colors.textMuted, fontSize: 12 }} />
                      <YAxis axisLine={false} tickLine={false} tick={{ fill: colors.textMuted, fontSize: 12 }} />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: colors.card, 
                          border: `1px solid ${colors.border}`,
                          borderRadius: '8px',
                          color: colors.text
                        }}
                        formatter={(value) => [`${value}%`, 'Sentiment']}
                      />
                      <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                        {[
                          { name: 'Positive', color: '#10b981' },
                          { name: 'Neutral', color: '#f59e0b' },
                          { name: 'Negative', color: '#ef4444' }
                        ].map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Rating Distribution */}
              <div style={{ 
                backgroundColor: colors.card,
                borderRadius: '12px',
                padding: '24px',
                border: `1px solid ${colors.border}`
              }}>
                <h3 style={{ margin: '0 0 20px 0', fontSize: '16px', fontWeight: '600' }}>Rating Distribution</h3>
                <div style={{ height: '250px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data.ratingDistribution}>
                      <CartesianGrid strokeDasharray="3 3" stroke={colors.border} vertical={false} />
                      <XAxis dataKey="rating" tickFormatter={(v) => `${v}★`} axisLine={false} tickLine={false} tick={{ fill: colors.textMuted, fontSize: 12 }} />
                      <YAxis axisLine={false} tickLine={false} tick={{ fill: colors.textMuted, fontSize: 12 }} />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: colors.card, 
                          border: `1px solid ${colors.border}`,
                          borderRadius: '8px',
                          color: colors.text
                        }}
                        formatter={(value, name, props) => [`${value} reviews`, 'Count']}
                      />
                      <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                        {data.ratingDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={getRatingColor(entry.rating)} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Trend Analysis */}
            <div style={{ 
              backgroundColor: colors.card,
              borderRadius: '12px',
              padding: '24px',
              border: `1px solid ${colors.border}`,
              marginTop: '24px'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '600' }}>Trend Analysis</h3>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button style={{ padding: '6px 12px', borderRadius: '6px', border: 'none', backgroundColor: '#10b981', color: 'white', fontSize: '12px' }}>Sentiment</button>
                  <button style={{ padding: '6px 12px', borderRadius: '6px', border: 'none', backgroundColor: colors.border, color: colors.text, fontSize: '12px' }}>Categories</button>
                </div>
              </div>
              <div style={{ height: '250px' }}>
                {(() => {
                  const trendMap = {};
                  reviews.forEach(r => {
                    if (!r.date) return;
                    if (!trendMap[r.date]) trendMap[r.date] = { date: r.date, total: 0, positive: 0, negative: 0, neutral: 0 };
                    trendMap[r.date].total++;
                    const s = (r.rating_label || '').toLowerCase();
                    if (s.includes('positive')) trendMap[r.date].positive++;
                    else if (s.includes('negative')) trendMap[r.date].negative++;
                    else trendMap[r.date].neutral++;
                  });
                  const trendData = Object.values(trendMap).sort((a, b) => a.date.localeCompare(b.date)).slice(-30);
                  if (trendData.length === 0) return <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: colors.textMuted }}><p>No trend data. Click Sync Reviews.</p></div>;
                  return (
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={trendData}>
                        <CartesianGrid strokeDasharray="3 3" stroke={colors.border} vertical={false} />
                        <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fill: colors.textMuted, fontSize: 11 }} tickFormatter={v => v.slice(5)} />
                        <YAxis axisLine={false} tickLine={false} tick={{ fill: colors.textMuted, fontSize: 11 }} />
                        <Tooltip contentStyle={{ backgroundColor: colors.card, border: `1px solid ${colors.border}`, borderRadius: '8px', color: colors.text }} />
                        <Legend />
                        <Line type="monotone" dataKey="positive" stroke="#10b981" strokeWidth={2} dot={false} name="Positive" />
                        <Line type="monotone" dataKey="negative" stroke="#ef4444" strokeWidth={2} dot={false} name="Negative" />
                        <Line type="monotone" dataKey="neutral" stroke="#f59e0b" strokeWidth={2} dot={false} name="Neutral" />
                      </LineChart>
                    </ResponsiveContainer>
                  );
                })()}
              </div>
            </div>
          </>
        )}

        {activeTab === 'categories' && (
          <>
            {/* Categories Header */}
            <div style={{ marginBottom: '24px' }}>
              <h2 style={{ margin: '0 0 8px 0', fontSize: '24px', fontWeight: '600' }}>Categories</h2>
              <p style={{ margin: 0, color: colors.textMuted }}>AI-identified themes and category distribution across Groww reviews</p>
            </div>

            {/* Filters */}
            <div style={{ 
              backgroundColor: colors.card,
              borderRadius: '12px',
              padding: '20px',
              marginBottom: '24px',
              border: `1px solid ${colors.border}`
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', gap: '40px' }}>
                  <div>
                    <p style={{ margin: '0 0 12px 0', fontSize: '12px', textTransform: 'uppercase', color: colors.textMuted, fontWeight: '600' }}>Platform</p>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      {['all', 'android', 'ios'].map(p => (
                        <button
                          key={p}
                          onClick={() => setPlatform(p)}
                          style={{
                            padding: '8px 16px',
                            borderRadius: '20px',
                            border: 'none',
                            backgroundColor: platform === p ? '#10b981' : colors.border,
                            color: platform === p ? 'white' : colors.text,
                            cursor: 'pointer',
                            fontSize: '13px',
                            textTransform: 'capitalize'
                          }}
                        >
                          {p}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p style={{ margin: '0 0 12px 0', fontSize: '12px', textTransform: 'uppercase', color: colors.textMuted, fontWeight: '600' }}>Time Period</p>
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                      {['Today', 'Yesterday', 'Last 7 Days', 'Last 15 Days', 'Last 30 Days'].map(period => (
                        <button
                          key={period}
                          onClick={() => setTimePeriod(period.toLowerCase().replace(/\s/g, ''))}
                          style={{
                            padding: '8px 16px',
                            borderRadius: '20px',
                            border: 'none',
                            backgroundColor: timePeriod === period.toLowerCase().replace(/\s/g, '') ? '#10b981' : colors.border,
                            color: timePeriod === period.toLowerCase().replace(/\s/g, '') ? 'white' : colors.text,
                            cursor: 'pointer',
                            fontSize: '13px'
                          }}
                        >
                          {period}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
                <button onClick={() => { setPlatform('all'); setTimePeriod('last30days'); }} style={{ color: colors.textMuted, fontSize: '13px', background: 'none', border: 'none', cursor: 'pointer' }}>Reset</button>
              </div>
            </div>

            {/* Category Charts */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
              <div style={{ 
                backgroundColor: colors.card,
                borderRadius: '12px',
                padding: '24px',
                border: `1px solid ${colors.border}`
              }}>
                <h3 style={{ margin: '0 0 20px 0', fontSize: '16px', fontWeight: '600' }}>Sentiment Analysis</h3>
                <div style={{ height: '250px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={[
                      { name: 'Positive', value: data.sentimentSplit?.positive || 0 },
                      { name: 'Neutral', value: data.sentimentSplit?.neutral || 0 },
                      { name: 'Negative', value: data.sentimentSplit?.negative || 0 }
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" stroke={colors.border} vertical={false} />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: colors.textMuted }} />
                      <YAxis axisLine={false} tickLine={false} tick={{ fill: colors.textMuted }} />
                      <Tooltip contentStyle={{ backgroundColor: colors.card, border: `1px solid ${colors.border}`, borderRadius: '8px', color: colors.text }} formatter={(value) => [`${value}%`, 'Sentiment']} />
                      <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                        {[{ color: '#10b981' }, { color: '#f59e0b' }, { color: '#ef4444' }].map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div style={{ 
                backgroundColor: colors.card,
                borderRadius: '12px',
                padding: '24px',
                border: `1px solid ${colors.border}`
              }}>
                <h3 style={{ margin: '0 0 20px 0', fontSize: '16px', fontWeight: '600' }}>Rating Distribution</h3>
                <div style={{ height: '250px' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data.ratingDistribution}>
                      <CartesianGrid strokeDasharray="3 3" stroke={colors.border} vertical={false} />
                      <XAxis dataKey="rating" tickFormatter={(v) => `${v}★`} axisLine={false} tickLine={false} tick={{ fill: colors.textMuted }} />
                      <YAxis axisLine={false} tickLine={false} tick={{ fill: colors.textMuted }} />
                      <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                        {data.ratingDistribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={getRatingColor(entry.rating)} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Trend Analysis */}
            <div style={{ 
              backgroundColor: colors.card,
              borderRadius: '12px',
              padding: '24px',
              border: `1px solid ${colors.border}`,
              marginTop: '24px'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '600' }}>Trend Analysis</h3>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button style={{ padding: '6px 12px', borderRadius: '6px', border: 'none', backgroundColor: colors.border, color: colors.text, fontSize: '12px' }}>Sentiment</button>
                  <button style={{ padding: '6px 12px', borderRadius: '6px', border: 'none', backgroundColor: '#10b981', color: 'white', fontSize: '12px' }}>Categories</button>
                </div>
              </div>
              <div style={{ height: '250px' }}>
                {(() => {
                  const trendMap = {};
                  reviews.forEach(r => {
                    if (!r.date) return;
                    if (!trendMap[r.date]) trendMap[r.date] = { date: r.date, positive: 0, negative: 0, neutral: 0 };
                    const s = (r.rating_label || '').toLowerCase();
                    if (s.includes('positive')) trendMap[r.date].positive++;
                    else if (s.includes('negative')) trendMap[r.date].negative++;
                    else trendMap[r.date].neutral++;
                  });
                  const trendData = Object.values(trendMap).sort((a, b) => a.date.localeCompare(b.date)).slice(-30);
                  if (trendData.length === 0) return <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: colors.textMuted }}><p>No trend data. Click Sync Reviews.</p></div>;
                  return (
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={trendData}>
                        <CartesianGrid strokeDasharray="3 3" stroke={colors.border} vertical={false} />
                        <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fill: colors.textMuted, fontSize: 11 }} tickFormatter={v => v.slice(5)} />
                        <YAxis axisLine={false} tickLine={false} tick={{ fill: colors.textMuted, fontSize: 11 }} />
                        <Tooltip contentStyle={{ backgroundColor: colors.card, border: `1px solid ${colors.border}`, borderRadius: '8px', color: colors.text }} />
                        <Legend />
                        <Line type="monotone" dataKey="positive" stroke="#10b981" strokeWidth={2} dot={false} name="Positive" />
                        <Line type="monotone" dataKey="negative" stroke="#ef4444" strokeWidth={2} dot={false} name="Negative" />
                        <Line type="monotone" dataKey="neutral" stroke="#f59e0b" strokeWidth={2} dot={false} name="Neutral" />
                      </LineChart>
                    </ResponsiveContainer>
                  );
                })()}
              </div>
            </div>
          </>
        )}

        {activeTab === 'wordcloud' && (
          <>
            <div style={{ marginBottom: '24px' }}>
              <h2 style={{ margin: '0 0 8px 0', fontSize: '24px', fontWeight: '600' }}>Word Cloud</h2>
              <p style={{ margin: 0, color: colors.textMuted }}>Most used words, top keywords, and top upvoted reviews</p>
            </div>

            {/* Filters */}
            <div style={{ 
              backgroundColor: colors.card,
              borderRadius: '12px',
              padding: '20px',
              marginBottom: '24px',
              border: `1px solid ${colors.border}`
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', gap: '40px' }}>
                  <div>
                    <p style={{ margin: '0 0 12px 0', fontSize: '12px', textTransform: 'uppercase', color: colors.textMuted, fontWeight: '600' }}>Platform</p>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      {['all', 'android', 'ios'].map(p => (
                        <button
                          key={p}
                          onClick={() => setPlatform(p)}
                          style={{
                            padding: '8px 16px',
                            borderRadius: '20px',
                            border: 'none',
                            backgroundColor: platform === p ? '#10b981' : colors.border,
                            color: platform === p ? 'white' : colors.text,
                            cursor: 'pointer',
                            fontSize: '13px',
                            textTransform: 'capitalize'
                          }}
                        >
                          {p}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p style={{ margin: '0 0 12px 0', fontSize: '12px', textTransform: 'uppercase', color: colors.textMuted, fontWeight: '600' }}>Time Period</p>
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                      {['Today', 'Yesterday', 'Last 7 Days', 'Last 15 Days', 'Last 30 Days'].map(period => (
                        <button
                          key={period}
                          onClick={() => setTimePeriod(period.toLowerCase().replace(/\s/g, ''))}
                          style={{
                            padding: '8px 16px',
                            borderRadius: '20px',
                            border: 'none',
                            backgroundColor: timePeriod === period.toLowerCase().replace(/\s/g, '') ? '#10b981' : colors.border,
                            color: timePeriod === period.toLowerCase().replace(/\s/g, '') ? 'white' : colors.text,
                            cursor: 'pointer',
                            fontSize: '13px'
                          }}
                        >
                          {period}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
                <button onClick={() => { setPlatform('all'); setTimePeriod('last30days'); }} style={{ color: colors.textMuted, fontSize: '13px', background: 'none', border: 'none', cursor: 'pointer' }}>Reset</button>
              </div>
            </div>

            {/* Dynamic Word Analysis & Stats Grid */}
            {(() => {
              const stopWords = new Set(['the','and','for','are','was','is','in','it','to','of','a','i','my','me','app','this','with','very','so','have','has','not','but','be','they','your','from','on','at','by','an','as','we','do','its','no','or','up','had','can','get','got','did','our','their','about','after','also','just','some','more','when','like','even','than','there','them','which','would','could','should']);
              let totalWords = 0;
              const freq = {};
              reviews.forEach(r => {
                const text = (r.review_text || r.content || '').toLowerCase();
                text.split(/\s+/).forEach(w => {
                  const clean = w.replace(/[^a-z]/g, '');
                  if (clean.length > 2) {
                    totalWords++;
                    if (!stopWords.has(clean)) {
                      freq[clean] = (freq[clean] || 0) + 1;
                    }
                  }
                });
              });
              const uniqueWords = Object.keys(freq).length;

              return (
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(3, 1fr)', 
                  gap: '16px',
                  marginBottom: '24px'
                }}>
                  <div style={{ 
                    backgroundColor: colors.card,
                    borderRadius: '12px',
                    padding: '20px',
                    border: `1px solid ${colors.border}`
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                      <MessageSquare size={16} color={colors.textMuted} />
                      <span style={{ fontSize: '12px', color: colors.textMuted, textTransform: 'uppercase' }}>Reviews Analyzed</span>
                    </div>
                    <p style={{ margin: 0, fontSize: '28px', fontWeight: '700' }}>{reviews.length.toLocaleString()}</p>
                  </div>

                  <div style={{ 
                    backgroundColor: colors.card,
                    borderRadius: '12px',
                    padding: '20px',
                    border: `1px solid ${colors.border}`
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                      <BarChart3 size={16} color="#8b5cf6" />
                      <span style={{ fontSize: '12px', color: colors.textMuted, textTransform: 'uppercase' }}>Total Words</span>
                    </div>
                    <p style={{ margin: 0, fontSize: '28px', fontWeight: '700' }}>{totalWords.toLocaleString()}</p>
                  </div>

                  <div style={{ 
                    backgroundColor: colors.card,
                    borderRadius: '12px',
                    padding: '20px',
                    border: `1px solid ${colors.border}`
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                      <PieChart size={16} color="#f59e0b" />
                      <span style={{ fontSize: '12px', color: colors.textMuted, textTransform: 'uppercase' }}>Unique Words</span>
                    </div>
                    <p style={{ margin: 0, fontSize: '28px', fontWeight: '700' }}>{uniqueWords.toLocaleString()}</p>
                  </div>
                </div>
              );
            })()}

            {/* Word Cloud Visualization */}
            <div style={{ 
              backgroundColor: colors.card,
              borderRadius: '12px',
              padding: '40px',
              border: `1px solid ${colors.border}`,
              minHeight: '400px'
            }}>
              <h3 style={{ margin: '0 0 24px 0', fontSize: '16px', fontWeight: '600' }}>Word Cloud</h3>
              <div style={{ 
                display: 'flex', 
                flexWrap: 'wrap', 
                alignItems: 'center', 
                justifyContent: 'center',
                gap: '12px',
                lineHeight: 1.4
              }}>
{(() => {
                  const stopWords = new Set(['the','and','for','are','was','is','in','it','to','of','a','i','my','me','app','this','with','very','so','have','has','not','but','be','they','your','from','on','at','by','an','as','we','do','its','no','or','up','had','can','get','got','did','our']);
                  const wordFreq = {};
                  reviews.forEach(r => {
                    const text = (r.review_text || r.content || '').toLowerCase();
                    text.split(/\s+/).forEach(w => {
                      const clean = w.replace(/[^a-z]/g, '');
                      if (clean.length > 3 && !stopWords.has(clean)) {
                        wordFreq[clean] = (wordFreq[clean] || 0) + 1;
                      }
                    });
                  });
                  const wordColors = ['#10b981','#3b82f6','#f59e0b','#8b5cf6','#06b6d4','#ef4444','#ec4899'];
                  const sorted = Object.entries(wordFreq).sort((a,b) => b[1]-a[1]).slice(0,40);
                  const maxCount = sorted[0]?.[1] || 1;
                  return sorted.map(([word, count], idx) => {
                    const size = Math.round(14 + (count / maxCount) * 34);
                    const color = wordColors[idx % wordColors.length];
                    return (
                      <span
                        key={idx}
                        title={`"${word}" appears ${count} times — click to search reviews`}
                        onClick={() => { setActiveTab('reviews'); setSearchQuery(word); }}
                        onMouseEnter={e => { e.target.style.transform = 'scale(1.2)'; e.target.style.opacity = '0.8'; }}
                        onMouseLeave={e => { e.target.style.transform = 'scale(1)'; e.target.style.opacity = '1'; }}
                        style={{
                          fontSize: size,
                          color,
                          fontWeight: size > 30 ? 700 : 500,
                          cursor: 'pointer',
                          transition: 'transform 0.2s, opacity 0.2s',
                          display: 'inline-block'
                        }}
                      >
                        {word}
                      </span>
                    );
                  });
                })()}
              </div>
            </div>
          </>
        )}

        {activeTab === 'ideation' && (
          <>
            <div style={{ marginBottom: '24px' }}>
              <h2 style={{ margin: '0 0 8px 0', fontSize: '24px', fontWeight: '600' }}>Ideation</h2>
              <p style={{ margin: 0, color: colors.textMuted }}>AI-generated feature ideas and improvement suggestions</p>
            </div>

            {data.actions && data.actions.length > 0 && (
              <div style={{ 
                backgroundColor: colors.card,
                borderRadius: '12px',
                padding: '24px',
                border: `1px solid ${colors.border}`
              }}>
                <h3 style={{ margin: '0 0 20px 0', fontSize: '16px', fontWeight: '600' }}>💡 Recommended Actions</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {data.actions.map((action, idx) => (
                    <div 
                      key={idx}
                      style={{
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '12px',
                        padding: '20px',
                        backgroundColor: darkMode ? '#1e293b' : '#f0fdf4',
                        borderRadius: '12px',
                        borderLeft: '4px solid #10b981'
                      }}
                    >
                      <div style={{ 
                        width: '32px', 
                        height: '32px', 
                        backgroundColor: '#10b981',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '14px',
                        fontWeight: '600',
                        color: 'white',
                        flexShrink: 0
                      }}>
                        {idx + 1}
                      </div>
                      <div>
                        <p style={{ margin: 0, color: colors.text, fontSize: '16px', lineHeight: 1.5 }}>{action}</p>
                        <p style={{ margin: '8px 0 0 0', fontSize: '13px', color: colors.textMuted }}>AI-generated from review analysis</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div style={{ 
              backgroundColor: colors.card,
              borderRadius: '12px',
              padding: '24px',
              border: `1px solid ${colors.border}`,
              marginTop: '24px'
            }}>
              <h3 style={{ margin: '0 0 20px 0', fontSize: '16px', fontWeight: '600' }}>Feature Requests</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {data.themes?.map((theme, idx) => (
                  <div 
                    key={idx}
                    style={{
                      padding: '16px',
                      backgroundColor: darkMode ? '#1e293b' : '#f8fafc',
                      borderRadius: '8px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                  >
                    <div>
                      <p style={{ margin: 0, fontWeight: '600' }}>{theme.label}</p>
                      <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: colors.textMuted }}>{theme.count} mentions</p>
                    </div>
                    <Zap size={20} color="#f59e0b" />
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {activeTab === 'reporting' && (
          <>
            {/* Header with Sync */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
              <div>
                <h2 style={{ margin: '0 0 8px 0', fontSize: '24px', fontWeight: '600' }}>Weekly Pulse</h2>
                <p style={{ margin: 0, color: colors.textMuted }}>
                  AI-powered App Review Pulse Dashboard
                  {lastSynced && (
                    <span style={{ marginLeft: '12px', fontSize: '12px' }}>
                      • Last synced: {lastSynced.toLocaleTimeString()}
                    </span>
                  )}
                </p>
                {newReviewsCount > 0 && (
                  <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#10b981' }}>
                    {newReviewsCount} new review{newReviewsCount > 1 ? 's' : ''} available
                  </p>
                )}
              </div>
              <button
                onClick={() => fetchData(true)}
                disabled={loading}
                style={{
                  padding: '10px 20px',
                  borderRadius: '8px',
                  border: 'none',
                  backgroundColor: '#10b981',
                  color: 'white',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontSize: '14px',
                  fontWeight: '500',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  opacity: loading ? 0.7 : 1
                }}
              >
                <RefreshCw size={16} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
                {loading ? 'Syncing...' : 'Sync Reviews'}
              </button>
            </div>

            {/* Filters */}
            <div style={{ 
              backgroundColor: colors.card,
              borderRadius: '12px',
              padding: '16px 20px',
              marginBottom: '24px',
              border: `1px solid ${colors.border}`,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div style={{ display: 'flex', gap: '40px' }}>
                <div>
                  <p style={{ margin: '0 0 8px 0', fontSize: '11px', textTransform: 'uppercase', color: colors.textMuted, fontWeight: '600', letterSpacing: '0.5px' }}>Platform</p>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    {['all', 'android', 'ios'].map(p => (
                      <button
                        key={p}
                        onClick={() => setPlatform(p)}
                        style={{
                          padding: '6px 14px',
                          borderRadius: '20px',
                          border: 'none',
                          backgroundColor: platform === p ? '#10b981' : colors.border,
                          color: platform === p ? 'white' : colors.text,
                          cursor: 'pointer',
                          fontSize: '13px',
                          textTransform: 'capitalize'
                        }}
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <p style={{ margin: '0 0 8px 0', fontSize: '11px', textTransform: 'uppercase', color: colors.textMuted, fontWeight: '600', letterSpacing: '0.5px' }}>Time Range</p>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    {['Today', '7 Days', '30 Days', '8-12 Weeks'].map(range => (
                      <button
                        key={range}
                        style={{
                          padding: '6px 14px',
                          borderRadius: '20px',
                          border: 'none',
                          backgroundColor: range === '8-12 Weeks' ? '#10b981' : colors.border,
                          color: range === '8-12 Weeks' ? 'white' : colors.text,
                          cursor: 'pointer',
                          fontSize: '13px'
                        }}
                      >
                        {range}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Weekly Pulse Note (Dynamic) */}
            {(() => {
              const headlineText = data.headline || 'Weekly review analysis highlights key user concerns and improvement opportunities';
              const topThemes = (data.themes || []).slice(0, 3);
              const quotesList = data.quotes || [];
              const actionsList = data.actions || [];
              const docTargetUrl = data.docsUrl || 'https://docs.google.com/document/d/1IsqpOHq53G51Shg5R271iq7P57k6wUqqQKVNzJVA6dw/edit';
              const recipient = data.recipient || 'support-team@groww.in';
              const todayStr = new Date().toISOString().split('T')[0];

              const pulseMarkdown = [
                `# Weekly App Review Pulse - ${todayStr}`,
                '',
                `**${headlineText}**`,
                '',
                '## Top 3 Themes',
                ...topThemes.map((t, idx) => `${idx + 1}. **${t.label || t.theme_name}** - ${t.description || t.summary || ''}`),
                '',
                '## Real User Quotes',
                ...quotesList.map(q => `- "${typeof q === 'object' ? q.quote : q}"`),
                '',
                '## Recommended Actions',
                ...actionsList.map((a, idx) => `${idx + 1}. ${typeof a === 'object' ? a.action : a}`)
              ].join('\n');

              const wordCount = pulseMarkdown.trim().split(/\s+/).filter(Boolean).length;

              return (
                <>
                  <div style={{ 
                    backgroundColor: colors.card,
                    borderRadius: '12px',
                    padding: '24px',
                    border: `1px solid ${colors.border}`,
                    marginBottom: '24px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <Zap size={20} color="#10b981" />
                        <div>
                          <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '600' }}>Weekly Pulse Note</h3>
                          <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: colors.textMuted }}>Executive one-pager · LIP limit ≤250 words</p>
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <span style={{ padding: '4px 10px', backgroundColor: darkMode ? '#1e293b' : '#f1f5f9', borderRadius: '4px', fontSize: '12px', color: colors.textMuted }}>{todayStr}</span>
                        <span style={{ padding: '4px 10px', backgroundColor: darkMode ? '#1e293b' : '#f1f5f9', borderRadius: '4px', fontSize: '12px', color: '#10b981' }}>{wordCount} words</span>
                      </div>
                    </div>

                    <div style={{ color: colors.text, fontSize: '14px', lineHeight: 1.7 }}>
                      <p style={{ margin: '0 0 16px 0', fontWeight: '500' }}>
                        {headlineText}
                      </p>

                      <h4 style={{ margin: '20px 0 12px 0', fontSize: '13px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.5px', color: colors.textMuted }}>Top 3 Themes</h4>
                      <ol style={{ margin: 0, paddingLeft: '20px', lineHeight: 1.8 }}>
                        {topThemes.map((theme, idx) => (
                          <li key={idx}>
                            <strong>{theme.label || theme.theme_name}</strong> — {theme.description || theme.summary || `${theme.count} mentions`}
                          </li>
                        ))}
                      </ol>

                      <h4 style={{ margin: '20px 0 12px 0', fontSize: '13px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.5px', color: colors.textMuted }}>Real User Quotes</h4>
                      <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: 1.8, color: colors.textMuted }}>
                        {quotesList.map((quote, idx) => (
                          <li key={idx}>"{typeof quote === 'object' ? quote.quote : quote}"</li>
                        ))}
                      </ul>

                      <h4 style={{ margin: '20px 0 12px 0', fontSize: '13px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.5px', color: colors.textMuted }}>Action Ideas</h4>
                      <ol style={{ margin: 0, paddingLeft: '20px', lineHeight: 1.8 }}>
                        {actionsList.map((action, idx) => (
                          <li key={idx}>{typeof action === 'object' ? action.action : action}</li>
                        ))}
                      </ol>
                    </div>
                  </div>

                  {/* Email Draft Preview */}
                  <div style={{ 
                    backgroundColor: colors.card,
                    borderRadius: '12px',
                    padding: '24px',
                    border: `1px solid ${colors.border}`
                  }}>
                    <h3 style={{ margin: '0 0 20px 0', fontSize: '14px', fontWeight: '600', color: '#10b981', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Email Draft Preview (MCP Integrated)</h3>
                    
                    <div style={{ marginBottom: '16px' }}>
                      <p style={{ margin: '0 0 8px 0', fontSize: '14px', color: colors.textMuted }}>
                        <span style={{ color: colors.textMuted }}>To: </span>
                        <span style={{ color: colors.text }}>{recipient}</span>
                      </p>
                      <p style={{ margin: 0, fontSize: '14px', color: colors.textMuted }}>
                        <span style={{ color: colors.textMuted }}>Subject: </span>
                        <span style={{ color: colors.text, fontWeight: '500' }}>Weekly App Review Pulse - {todayStr}</span>
                      </p>
                    </div>

                    <div style={{ 
                      backgroundColor: darkMode ? '#0f172a' : '#f8fafc',
                      borderRadius: '8px',
                      padding: '20px',
                      marginBottom: '24px',
                      fontSize: '14px',
                      lineHeight: 1.7,
                      color: colors.text
                    }}>
                      <p style={{ margin: '0 0 12px 0' }}>{headlineText}</p>
                      <p style={{ margin: '0 0 8px 0', fontWeight: '600' }}>TOP 3 THEMES</p>
                      <ol style={{ margin: '0 0 16px 0', paddingLeft: '20px' }}>
                        {topThemes.map((t, idx) => (
                          <li key={idx}>{t.label || t.theme_name} — {t.description || t.summary || `${t.count} reviews`}</li>
                        ))}
                      </ol>
                      <p style={{ margin: '0 0 8px 0', fontWeight: '600' }}>REAL USER QUOTES</p>
                      <ul style={{ margin: '0 0 16px 0', paddingLeft: '20px', color: colors.textMuted }}>
                        {quotesList.map((q, idx) => (
                          <li key={idx}>"{typeof q === 'object' ? q.quote : q}"</li>
                        ))}
                      </ul>
                      <p style={{ margin: '0 0 8px 0', fontWeight: '600' }}>RECOMMENDED ACTIONS</p>
                      <ol style={{ margin: 0, paddingLeft: '20px' }}>
                        {actionsList.map((a, idx) => (
                          <li key={idx}>{typeof a === 'object' ? a.action : a}</li>
                        ))}
                      </ol>
                    </div>

                    <div style={{ display: 'flex', gap: '12px' }}>
                      <button
                        onClick={() => {
                          const subject = `Weekly App Review Pulse - ${todayStr}`;
                          window.location.href = `mailto:${recipient}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(pulseMarkdown)}`;
                        }}
                        style={{
                          padding: '12px 24px',
                          borderRadius: '8px',
                          border: 'none',
                          backgroundColor: '#10b981',
                          color: 'white',
                          cursor: 'pointer',
                          fontSize: '14px',
                          fontWeight: '500',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px'
                        }}
                      >
                        <Mail size={16} />
                        Draft Email
                      </button>
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(pulseMarkdown).then(() => {
                            alert('Content copied to clipboard! Opening Google Docs...');
                            window.open(docTargetUrl, '_blank');
                          });
                        }}
                        style={{
                          padding: '12px 24px',
                          borderRadius: '8px',
                          border: `1px solid ${colors.border}`,
                          backgroundColor: colors.card,
                          color: colors.text,
                          cursor: 'pointer',
                          fontSize: '14px',
                          fontWeight: '500',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px'
                        }}
                      >
                        <FileText size={16} />
                        Append to Docs
                      </button>
                    </div>
                  </div>
                </>
              );
            })()}
          </>
        )}
      </main>
    </div>
  );
}

export default App;
