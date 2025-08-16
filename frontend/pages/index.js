'use client';

import Head from "next/head";
import { Geist, Geist_Mono } from "next/font/google";
import { ChatGame } from "../components/Game";
import styles from "@/styles/Home.module.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export default function Home() {
  return (
    <>
      <Head>
        <title>Chat Your Game</title>
        <meta name="description" content="Interactive text adventure game" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main className={`${styles.page} ${geistSans.variable} ${geistMono.variable}`}>
        <ChatGame />
      </main>
    </>
  );
}
