import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Image as ImageIcon, Heart, Download, Share } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "@/hooks/use-toast";
import { motion } from "framer-motion";
import api from '../api/client';

interface ImageData {
  id: string;
  title: string;
  category: string;
  url: string;
  likes: number;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      delayChildren: 0.3,
      staggerChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { y: 20, opacity: 0 },
  visible: {
    y: 0,
    opacity: 1,
    transition: { type: "spring", stiffness: 300, damping: 24 }
  }
};

const Gallery = () => {
  const [images, setImages] = useState<ImageData[]>([]);
  const [liked, setLiked] = useState<Set<string>>(new Set());

  useEffect(() => {
    const fetchImages = async () => {
      try {
        const response = await api.get('/gallery/all');
        setImages(response.data);
      } catch (error) {
        console.error('Failed to fetch gallery:', error);
      }
    };
    fetchImages();
  }, []);

  const handleLikeImage = async (id: string) => {
    try {
      await api.post(`/gallery/like/${id}`);
      setImages(prev =>
        prev.map(img =>
          img.id === id ? { ...img, likes: img.likes === 0 ? 1 : img.likes - 1 } : img
        )
      );
      setLiked(prev => {
        const newLiked = new Set(prev);
        if (newLiked.has(id)) {
          newLiked.delete(id);
          toast({
            title: "Image removed from favorites",
            description: "This image has been removed from your favorites.",
          });
        } else {
          newLiked.add(id);
          toast({
            title: "Image liked!",
            description: "This image has been added to your favorites.",
          });
        }
        return newLiked;
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.error || "Failed to toggle like",
      });
    }
  };

  const filteredImages = (category: string) =>
    category === 'all' ? images : images.filter(img => img.category === category);

  return (
    <motion.div 
      initial="hidden"
      animate="visible"
      variants={containerVariants}
      className="min-h-screen bg-gradient-to-b from-background via-background/95 to-background/90"
    >
      <div className="container mx-auto px-4 py-12">
        <motion.div 
          variants={itemVariants}
          className="flex flex-col items-center text-center mb-12"
        >
          <Badge variant="outline" className="mb-4 p-1 px-3 border-primary/30 bg-primary/5">
            <ImageIcon className="h-3.5 w-3.5 mr-2 text-primary" />
            Gallery
          </Badge>
          <motion.h1 
            className="text-4xl md:text-5xl font-bold tracking-tight mb-4 bg-gradient-to-r from-primary via-purple-500 to-indigo-400 bg-clip-text text-transparent"
            animate={{ 
              backgroundPosition: ["0% center", "100% center", "0% center"], 
            }}
            transition={{ 
              duration: 8, 
              repeat: Infinity, 
              repeatType: "mirror" 
            }}
          >
            Creative Collection
          </motion.h1>
          <motion.p 
            variants={itemVariants}
            className="text-xl text-muted-foreground max-w-2xl mb-8"
          >
            Browse through our collection of AI-generated images created by our community.
          </motion.p>
        </motion.div>

        <Tabs defaultValue="all" className="w-full max-w-6xl mx-auto">
          <motion.div variants={itemVariants}>
            <TabsList className="grid grid-cols-4 mb-8 w-full md:w-auto rounded-full p-1 bg-muted/50">
              <TabsTrigger value="all" className="rounded-full data-[state=active]:bg-background data-[state=active]:shadow-sm">All Images</TabsTrigger>
              <TabsTrigger value="nature" className="rounded-full data-[state=active]:bg-background data-[state=active]:shadow-sm">Nature</TabsTrigger>
              <TabsTrigger value="urban" className="rounded-full data-[state=active]:bg-background data-[state=active]:shadow-sm">Urban</TabsTrigger>
              <TabsTrigger value="art" className="rounded-full data-[state=active]:bg-background data-[state=active]:shadow-sm">Art</TabsTrigger>
            </TabsList>
          </motion.div>

          {['all', 'nature', 'urban', 'art'].map(category => (
            <TabsContent key={category} value={category} className="mt-6">
              <motion.div 
                variants={containerVariants}
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
              >
                {filteredImages(category).map((image) => (
                  <motion.div 
                    key={image.id}
                    variants={itemVariants}
                    whileHover={{ y: -10 }}
                    transition={{ type: "spring", stiffness: 300, damping: 24 }}
                  >
                    <Card className="overflow-hidden transition-all hover:shadow-lg border-none rounded-xl">
                      <CardHeader className="p-0">
                        <div className="aspect-video w-full overflow-hidden">
                          <motion.img 
                            src={image.url} 
                            alt={image.title} 
                            className="w-full h-full object-cover transition-transform hover:scale-105" 
                            whileHover={{ scale: 1.05 }}
                            transition={{ duration: 0.3 }}
                          />
                        </div>
                      </CardHeader>
                      <CardContent className="p-5">
                        <CardTitle className="text-lg mb-2">{image.title}</CardTitle>
                        <Badge variant="outline" className="bg-primary/5 text-primary border-primary/10">
                          {image.category}
                        </Badge>
                      </CardContent>
                      <CardFooter className="p-5 pt-0 flex justify-between">
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          onClick={() => handleLikeImage(image.id)}
                          className={liked.has(image.id) ? "text-red-500" : ""}
                        >
                          <Heart className={`h-4 w-4 mr-2 ${liked.has(image.id) ? "fill-current" : ""}`} />
                          {image.likes}
                        </Button>
                        <div className="flex gap-2">
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <Download className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <Share className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardFooter>
                    </Card>
                  </motion.div>
                ))}
              </motion.div>
            </TabsContent>
          ))}
        </Tabs>
      </div>
    </motion.div>
  );
};

export default Gallery;