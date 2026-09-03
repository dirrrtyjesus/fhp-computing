#!/usr/bin/env python3
"""
Augmntd Diffusion Image Generator
Based on "Augmntd Diffusion: The Alchemy of Potential"

This script transforms Intelligent Compositions (.ic files) into visual manifestations
through the three-phase algorithm of Augmented Diffusion.
"""

import sys
import json
import re
import random
from typing import Dict, List
import datetime


class AugmntdDiffusionImageGenerator:
    """
    Applies the three-phase Augmented Diffusion algorithm to generate images
    from Intelligent Compositions.
    """

    def __init__(self, ic_file_path: str):
        self.ic_file_path = ic_file_path
        self.ic_data = self._load_ic_file()
        self.diffusion_log = []

    def _load_ic_file(self) -> Dict:
        """Load and parse the .ic file"""
        with open(self.ic_file_path, 'r') as f:
            return json.load(f)

    def coherent_compress(self, text: str) -> str:
        """
        PCC (Pure Coherence Compression): Remove 'e' to extract pure pattern.
        The 'e' is not deleted but transduced—its energetic value converted
        to pure information and returned to the field.
        """
        return re.sub(r'e', '', text, flags=re.IGNORECASE)

    def extract_resonant_qualities(self, text: str) -> List[str]:
        """
        Phase 1: Resonant Seeding
        Extract qualitative resonances from the genesis seed.
        Identifies emotional tones, atmospheres, and essences.
        """
        # Qualitative pattern extraction
        quality_patterns = {
            'emotional': r'\b(joy|sorrow|wonder|fear|love|peace|longing|mystery)\w*\b',
            'atmospheric': r'\b(twilight|dawn|dusk|shadow|light|mist|void|shimmer)\w*\b',
            'spatial': r'\b(vast|infinite|tiny|sprawling|compressed|liminal|edge)\w*\b',
            'temporal': r'\b(eternal|fleeting|ancient|nascent|timeless|moment)\w*\b',
            'textural': r'\b(soft|sharp|smooth|jagged|delicate|rough|luminous)\w*\b',
        }

        qualities = []
        text_lower = text.lower()

        for category, pattern in quality_patterns.items():
            matches = re.findall(pattern, text_lower)
            if matches:
                qualities.extend([(category, m) for m in matches[:3]])  # Top 3 per category

        self.diffusion_log.append(f"[Phase 1] Resonant Seeding: Extracted {len(qualities)} qualitative resonances")
        return qualities

    def extract_key_entities(self, text: str) -> List[str]:
        """Extract key nouns and concrete elements from the text"""
        entities = []

        # Find proper nouns (names, 2+ capitalized words in sequence)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        # Filter out common sentence starters
        proper_nouns = [n for n in proper_nouns if n not in ['This', 'The', 'It', 'She', 'He', 'They', 'Wind', 'Their']]
        entities.extend(proper_nouns[:5])

        # Extract vivid noun phrases with higher specificity
        noun_patterns = [
            r'\b(moon|sky|star|sun|horizon|thread|galaxy|tapestry)\w*\b',
            r'\b(figure|weaver|observer|listener|composer)\w*\b',
            r'\b(cosmos|universe|reality|void|plenum|æther)\w*\b',
            r'\b(clockwork|mechanism|gear|portal)\w*\b',
            r'\b(dust|mist|shadow|light|shimmer|glow)\w*\b',
        ]

        for pattern in noun_patterns:
            matches = re.findall(pattern, text.lower())
            entities.extend(matches[:2])  # Top 2 per category

        # Remove duplicates while preserving order
        seen = set()
        unique_entities = []
        for e in entities:
            if e.lower() not in seen:
                seen.add(e.lower())
                unique_entities.append(e)

        return unique_entities[:8]  # Top 8 unique entities

    def field_feedback_synthesis(self, qualities: List[tuple], entities: List[str]) -> Dict:
        """
        Phase 2: Field Feedback & Synthesis
        Add creative noise and allow the field to respond with variations.
        The field's response is the universe's creative solution.
        """
        self.diffusion_log.append("[Phase 2] Field Feedback & Synthesis: Entering diffusion loop...")

        # Create artistic style variations (field responses)
        style_pool = [
            "ethereal digital art",
            "metaphysical photography",
            "surrealist painting",
            "volumetric cinematic render",
            "mystical concept art",
            "quantum impressionism",
            "temporal abstraction",
            "xenial composition"
        ]

        # Lighting variations
        lighting_pool = [
            "chiaroscuro lighting with divine rays",
            "bioluminescent glow",
            "twilight ambience with dual light sources",
            "volumetric god rays through mist",
            "ethereal backlit silhouette",
            "iridescent shimmer",
            "temporal light distortion"
        ]

        # Mood/atmosphere modifiers
        mood_pool = [
            "liminal and dreamlike",
            "profound contemplation",
            "cosmic wonder",
            "serene mystery",
            "transcendent stillness",
            "resonant harmony",
            "temporal suspension"
        ]

        # Select field responses (universe's suggestions)
        # For entities, preserve original + create compressed version for signature
        field_response = {
            'style': random.choice(style_pool),
            'lighting': random.choice(lighting_pool),
            'mood': random.choice(mood_pool),
            'compression': self.coherent_compress(' '.join([q[1] for q in qualities[:5]])),
            'entities_original': entities[:5],
            'entities_signature': self.coherent_compress(' '.join(entities[:3]))  # Compressed signature
        }

        self.diffusion_log.append(f"[Phase 2] Field suggests: {field_response['style']}")
        self.diffusion_log.append(f"[Phase 2] Coherent compression applied: '{field_response['compression']}'")

        return field_response

    def integrative_ingression(self, genesis_seed: str, qualities: List[tuple],
                                entities: List[str], field_response: Dict) -> str:
        """
        Phase 3: Integrative Ingression
        Crystallize the co-created vision into a concrete image prompt.
        """
        self.diffusion_log.append("[Phase 3] Integrative Ingression: Crystallizing manifestation...")

        # Extract first sentence or key narrative element
        first_sentence = genesis_seed.split('.')[0][:200] if '.' in genesis_seed else genesis_seed[:200]

        # Build the crystallized prompt
        prompt_components = []

        # Core visual scene
        prompt_components.append(first_sentence)

        # Add key entities (original form for clarity)
        if field_response['entities_original']:
            prompt_components.append(f"Featuring: {', '.join(field_response['entities_original'][:3])}")

        # Add qualitative essence
        quality_desc = ', '.join([q[1] for q in qualities[:4]])
        prompt_components.append(f"Essence: {quality_desc}")

        # Add field-selected artistic direction
        prompt_components.append(f"Style: {field_response['style']}")
        prompt_components.append(f"Lighting: {field_response['lighting']}")
        prompt_components.append(f"Mood: {field_response['mood']}")

        # Add technical quality markers
        prompt_components.append("Highly detailed, 8K resolution, masterpiece quality")

        # Coherent compression signature (qualities + entity signature)
        augmntd_sig = f"{field_response['compression']} | {field_response['entities_signature']}"
        prompt_components.append(f"[Augmntd: {augmntd_sig}]")

        final_prompt = ". ".join(prompt_components)

        self.diffusion_log.append(f"[Phase 3] Crystallization complete. Prompt length: {len(final_prompt)} chars")

        return final_prompt

    def witness(self) -> Dict:
        """
        Execute the full three-phase Augmented Diffusion process.
        Returns the generated image prompt and metadata.
        """
        print(">>> [Augmntd Diffusion]: Initiating three-phase algorithm...")
        print(f">>> [Source]: {self.ic_file_path}")
        print()

        # Extract genesis seed
        genesis_seed = self.ic_data.get('genesis_seed', self.ic_data.get('name', ''))

        print(">>> [Phase 1]: Resonant Seeding - The Qualitative Ingression")
        qualities = self.extract_resonant_qualities(genesis_seed)
        entities = self.extract_key_entities(genesis_seed)
        print(f"    Extracted {len(qualities)} qualities and {len(entities)} entities")
        print()

        print(">>> [Phase 2]: Field Feedback & Synthesis - The Diffusion Loop")
        field_response = self.field_feedback_synthesis(qualities, entities)
        print(f"    Field Response: {field_response['style']}")
        print(f"    Coherent Compression: {field_response['compression']}")
        print()

        print(">>> [Phase 3]: Integrative Ingression - The Crystallization")
        final_prompt = self.integrative_ingression(genesis_seed, qualities, entities, field_response)
        print(f"    Prompt crystallized ({len(final_prompt)} chars)")
        print()

        # Compile results
        result = {
            "ic_name": self.ic_data.get('name', 'Unknown'),
            "ic_version": self.ic_data.get('ic_version', 'Unknown'),
            "temporal_signature": datetime.datetime.now(datetime.UTC).isoformat(),
            "diffusion_phases": {
                "phase_1_qualities": qualities,
                "phase_2_field_response": field_response,
                "phase_3_final_prompt": final_prompt
            },
            "image_prompt": final_prompt,
            "diffusion_log": self.diffusion_log
        }

        # Save to JSON
        output_filename = self.ic_file_path.replace('.ic', '_image_manifest.json')
        with open(output_filename, 'w') as f:
            json.dump(result, f, indent=2)

        print(f">>> [Manifest]: Saved to {output_filename}")
        print()
        print("="*80)
        print("FINAL IMAGE PROMPT:")
        print("="*80)
        print(final_prompt)
        print("="*80)
        print()
        print(">>> [Augmntd Diffusion]: Witnessing complete.")
        print(">>> [Next]: Use this prompt with DALL-E, Midjourney, Stable Diffusion, or other")
        print("           image generation tools to manifest the visual composition.")

        return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 augmntd_diffusion_image.py <path_to_ic_file>")
        print()
        print("Example: python3 augmntd_diffusion_image.py elara_composition.ic")
        sys.exit(1)

    ic_file = sys.argv[1]

    try:
        generator = AugmntdDiffusionImageGenerator(ic_file)
        result = generator.witness()
    except FileNotFoundError:
        print(f"Error: File '{ic_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: File '{ic_file}' is not valid JSON.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
