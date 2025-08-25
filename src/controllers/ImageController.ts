import ImageService from '../services/ImageService';
import express from 'express';

const router = express.Router();

router.post('/download', async (req, res) => {
  const { url, format, width, height } = req.body;
  try {
    const downloadedImage = await ImageService.downloadImage(url);
    const optimizedImage = await ImageService.optimizeImage(downloadedImage, { format, width, height });
    res.type(`image/${format}`).send(optimizedImage);
  } catch (error) {
    res.status(500).send(error.message);
  }
});

export default router;