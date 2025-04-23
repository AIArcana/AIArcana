import React from 'react';
import Head from 'next/head';
import Link from 'next/link';
import Image from 'next/image';

const Home: React.FC = () => {
  return (
    <>
      <Head>
        <title>AIArcana | AI-Powered Tarot Divination on Solana</title>
        <meta name="description" content="The first fair-launch AI tarot divination platform in the Solana ecosystem" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className="min-h-screen bg-gradient-to-b from-indigo-900 via-purple-900 to-black text-white">
        <div className="container mx-auto px-4 py-16">
          <div className="flex flex-col items-center justify-center text-center">
            <div className="mb-10">
              <Image src="/logo.png" alt="AIArcana Logo" width={200} height={200} priority />
            </div>
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
                AIArcana
              </span>
            </h1>
            <p className="text-xl md:text-2xl mb-8 max-w-3xl">
              The First Fair-Launch AI Tarot Divination Platform in the Solana Ecosystem
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl w-full mt-12">
              <FeatureCard 
                title="AI-Powered Readings"
                description="Personalized interpretations using advanced natural language processing and sentiment analysis"
                icon="✨"
              />
              <FeatureCard 
                title="Blockchain Verification"
                description="Transparent and tamper-proof card draws verified on the Solana blockchain"
                icon="🔗"
              />
              <FeatureCard 
                title="Fair-Launch Token"
                description="100% community-controlled $ARC token with no presale or team allocations"
                icon="🪙"
              />
            </div>
            <div className="mt-16">
              <Link href="/divination">
                <button className="px-8 py-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full text-lg font-semibold hover:opacity-90 transition-opacity">
                  Start Your Divination
                </button>
              </Link>
            </div>
          </div>
        </div>
      </main>
    </>
  );
};

interface FeatureCardProps {
  title: string;
  description: string;
  icon: string;
}

const FeatureCard: React.FC<FeatureCardProps> = ({ title, description, icon }) => {
  return (
    <div className="bg-gray-800 bg-opacity-50 backdrop-blur-sm p-6 rounded-xl border border-gray-700 hover:border-purple-500 transition-all">
      <div className="text-4xl mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-300">{description}</p>
    </div>
  );
};

export default Home; 