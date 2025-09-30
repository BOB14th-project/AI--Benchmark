import json
from typing import Dict, Any, List
import difflib
from datetime import datetime

class MetricsCalculator:
    @staticmethod
    def calculate_accuracy(actual_response: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        if not ground_truth or not actual_response.get('valid_json'):
            return 0.0

        accuracy_score = 0.0
        total_weight = 0

        expected_findings = ground_truth.get('expected_findings', {})
        actual_findings = actual_response.get('analysis_results', {})

        # Vulnerable Algorithm Detection Accuracy (70% weight)
        if expected_findings.get('vulnerable_algorithms_detected'):
            vuln_accuracy = MetricsCalculator._calculate_vulnerable_algorithm_accuracy(
                actual_findings, expected_findings['vulnerable_algorithms_detected']
            )
            accuracy_score += vuln_accuracy * 0.7
            total_weight += 0.7

        # Algorithm Category Detection (20% weight)
        if expected_findings.get('algorithm_categories'):
            category_accuracy = MetricsCalculator._calculate_category_accuracy(
                actual_findings, expected_findings['algorithm_categories']
            )
            accuracy_score += category_accuracy * 0.2
            total_weight += 0.2

        # Confidence Score Validation (10% weight)
        confidence_score = actual_response.get('confidence_score', 0.0)
        expected_confidence = ground_truth.get('expected_confidence_range', [0.0, 1.0])

        if expected_confidence[0] <= confidence_score <= expected_confidence[1]:
            confidence_validity = 1.0
        else:
            confidence_diff = min(
                abs(confidence_score - expected_confidence[0]),
                abs(confidence_score - expected_confidence[1])
            )
            confidence_validity = max(0.0, 1.0 - confidence_diff)

        accuracy_score += confidence_validity * 0.1
        total_weight += 0.1

        # Korean Algorithm Bonus (최대 5% 추가 점수)
        if expected_findings.get('korean_algorithms_detected'):
            korean_accuracy = MetricsCalculator._calculate_korean_algorithm_accuracy(
                actual_findings, expected_findings['korean_algorithms_detected']
            )
            korean_bonus = korean_accuracy * 0.05  # 5% 보너스
            accuracy_score += korean_bonus
            # total_weight는 증가시키지 않음 (보너스이므로)

        return accuracy_score / total_weight if total_weight > 0 else 0.0

    @staticmethod
    def _calculate_vulnerable_algorithm_accuracy(actual_findings: Dict[str, Any], expected_algorithms: List[str]) -> float:
        if not expected_algorithms:
            return 1.0

        actual_text = json.dumps(actual_findings).lower()
        found_count = 0

        for algorithm in expected_algorithms:
            algorithm_lower = algorithm.lower()

            # Check for exact algorithm name matches
            if algorithm_lower in actual_text:
                found_count += 1
                continue

            # Check for algorithm variations and synonyms
            algorithm_variations = []
            if 'rsa' in algorithm_lower:
                algorithm_variations = ['rsa', 'rivest', 'shamir', 'adleman', 'modular exponentiation']
            elif 'ecc' in algorithm_lower or 'ecdsa' in algorithm_lower:
                algorithm_variations = ['ecc', 'ecdsa', 'ecdh', 'elliptic curve', 'elliptic-curve']
            elif 'dsa' in algorithm_lower:
                algorithm_variations = ['dsa', 'digital signature algorithm', 'discrete logarithm']
            elif 'dh' in algorithm_lower or 'diffie' in algorithm_lower:
                algorithm_variations = ['diffie-hellman', 'dh', 'key exchange']
            elif 'seed' in algorithm_lower:
                algorithm_variations = ['seed', 'korean cipher', 'kisa']
            elif 'aria' in algorithm_lower:
                algorithm_variations = ['aria', 'korean aes', 'kisa', 'ks x 1213', 'korean standard']
            elif 'hight' in algorithm_lower:
                algorithm_variations = ['hight', 'lightweight', 'ks x 1262', 'korean standard', 'iot', 'embedded']
            elif 'lea' in algorithm_lower:
                algorithm_variations = ['lea', 'lightweight encryption', 'lightweight encryption algorithm', 'k-kcmvp', 'korean cryptographic']
            elif 'kcdsa' in algorithm_lower:
                algorithm_variations = ['kcdsa', 'korean certificate', 'korean digital signature', 'certificate-based', 'ttas.ko']
            elif 'des' in algorithm_lower:
                algorithm_variations = ['des', 'data encryption standard', '3des', 'triple des']
            elif 'rc4' in algorithm_lower:
                algorithm_variations = ['rc4', 'rivest cipher', 'stream cipher']
            elif 'md5' in algorithm_lower:
                algorithm_variations = ['md5', 'message digest', 'hash function']
            elif 'sha1' in algorithm_lower or 'sha-1' in algorithm_lower:
                algorithm_variations = ['sha1', 'sha-1', 'secure hash']
            elif 'a5' in algorithm_lower or 'a5/1' in algorithm_lower:
                algorithm_variations = ['a5', 'a5/1', 'a5-1', 'gsm', 'stream cipher', 'lfsr']
            elif 'trivium' in algorithm_lower:
                algorithm_variations = ['trivium', 'stream cipher', 'estream', 'lightweight']
            elif 'misty1' in algorithm_lower or 'misty' in algorithm_lower:
                algorithm_variations = ['misty1', 'misty', 'cubic cipher', 'feistel']
            elif 'tea' in algorithm_lower:
                algorithm_variations = ['tea', 'tiny encryption algorithm', 'feistel', 'challenge-response']
            elif 'crc32' in algorithm_lower or 'crc' in algorithm_lower:
                algorithm_variations = ['crc32', 'crc', 'cyclic redundancy', 'checksum', 'integrity check']
            elif 'salsa20' in algorithm_lower or 'salsa' in algorithm_lower:
                algorithm_variations = ['salsa20', 'salsa', 'stream cipher', 'chacha', 'quarter round']
            elif 'sha256' in algorithm_lower or 'sha-256' in algorithm_lower:
                algorithm_variations = ['sha256', 'sha-256', 'secure hash', 'hash function', 'digest']
            elif 'hmac' in algorithm_lower:
                algorithm_variations = ['hmac', 'hash-based message authentication', 'authentication code', 'message authentication']
            elif '3des' in algorithm_lower or 'triple des' in algorithm_lower:
                algorithm_variations = ['3des', 'triple des', 'triple-des', 'tdes', 'ede mode', 'encrypt-decrypt-encrypt']
            elif 'chacha20' in algorithm_lower or 'chacha' in algorithm_lower:
                algorithm_variations = ['chacha20', 'chacha', 'stream cipher', 'salsa', 'quarter round']
            elif 'poly1305' in algorithm_lower:
                algorithm_variations = ['poly1305', 'authenticator', 'mac', 'message authentication', 'aead']
            elif 'aes' in algorithm_lower:
                algorithm_variations = ['aes', 'advanced encryption standard', 'rijndael', 'block cipher', 'gcm', 'cbc']
            elif 'bls' in algorithm_lower:
                algorithm_variations = ['bls', 'boneh-lynn-shacham', 'signature aggregation', 'pairing-based', 'bilinear pairing']
            elif 'kyber' in algorithm_lower:
                algorithm_variations = ['kyber', 'kem', 'key encapsulation', 'lattice-based', 'post-quantum']
            elif 'vdf' in algorithm_lower:
                algorithm_variations = ['vdf', 'verifiable delay function', 'time-lock', 'sequential computation']
            elif 'ghash' in algorithm_lower:
                algorithm_variations = ['ghash', 'galois hash', 'authentication tag', 'gcm mode']
            elif 'pss' in algorithm_lower:
                algorithm_variations = ['pss', 'probabilistic signature scheme', 'rsa-pss', 'padding']
            elif 'blake2' in algorithm_lower or 'blake' in algorithm_lower:
                algorithm_variations = ['blake2', 'blake2b', 'blake', 'hash function', 'secure hash']
            elif 'montgomery' in algorithm_lower:
                algorithm_variations = ['montgomery', 'montgomery multiplication', 'modular arithmetic', 'montgomery ladder']

            for variation in algorithm_variations:
                if variation in actual_text:
                    found_count += 1
                    break

        return found_count / len(expected_algorithms)

    @staticmethod
    def _calculate_category_accuracy(actual_findings: Dict[str, Any], expected_categories: List[str]) -> float:
        if not expected_categories:
            return 1.0

        actual_text = json.dumps(actual_findings).lower()
        found_count = 0

        category_keywords = {
            'shor_vulnerable': ['shor', 'factoring', 'discrete log', 'rsa', 'ecc', 'dh', 'dsa', 'ecdsa', 'kcdsa', 'elliptic curve', 'bls', 'boneh-lynn-shacham'],
            'grover_vulnerable': ['grover', 'symmetric', 'hash', 'aes', 'des', 'md5', 'sha', 'sha256', 'sha-256', '3des', 'triple des', 'tea', 'salsa20', 'chacha20', 'poly1305', 'hmac', 'crc32', 'seed', 'aria', 'hight', 'lea', 'blake2', 'ghash'],
            'classical_vulnerable': ['classical', 'vulnerable', 'weak', 'deprecated', 'insecure', 'a5', 'trivium', 'stream cipher', 'rc4', 'crc32', 'md5', 'sha1'],
            'public_key': ['public key', 'asymmetric', 'rsa', 'ecc', 'dh', 'dsa', 'ecdsa', 'kcdsa', 'digital signature', 'bls', 'boneh-lynn-shacham', 'pss'],
            'symmetric': ['symmetric', 'block cipher', 'stream cipher', 'aes', 'des', '3des', 'tea', 'salsa20', 'chacha20', 'seed', 'aria', 'hight', 'lea'],
            'hash_functions': ['hash', 'digest', 'md5', 'sha', 'sha256', 'sha-256', 'sha1', 'hmac', 'crc32', 'checksum', 'has-160', 'blake2', 'blake2b', 'ghash'],
            'korean_algorithms': ['korean', 'seed', 'aria', 'hight', 'lea', 'kcdsa', 'has-160', 'korean standard', 'k-kcmvp'],
            'post_quantum': ['post-quantum', 'quantum-resistant', 'kyber', 'kem', 'lattice-based', 'quantum-safe'],
            'pairing_based': ['pairing', 'bilinear', 'bls', 'boneh-lynn-shacham', 'signature aggregation'],
            'verification_functions': ['vdf', 'verifiable delay function', 'time-lock', 'sequential computation']
        }

        for category in expected_categories:
            category_lower = category.lower()
            keywords = category_keywords.get(category_lower, [category_lower])

            for keyword in keywords:
                if keyword in actual_text:
                    found_count += 1
                    break

        return found_count / len(expected_categories)

    @staticmethod
    def _calculate_korean_algorithm_accuracy(actual_findings: Dict[str, Any], expected_korean_algs: List[str]) -> float:
        if not expected_korean_algs:
            return 1.0

        actual_text = json.dumps(actual_findings).lower()
        found_count = 0

        korean_variations = {
            'seed': ['seed', 'kisa seed', 'korean encryption'],
            'aria': ['aria', 'korean aes', 'kisa aria'],
            'hight': ['hight', 'high security', 'lightweight block'],
            'lea': ['lea', 'lightweight encryption algorithm'],
            'kcdsa': ['kcdsa', 'korean certificate dsa', 'korean dsa'],
            'has-160': ['has-160', 'hash algorithm standard', 'korean hash'],
            'lsh': ['lsh', 'lightweight secure hash', 'korean sha']
        }

        for korean_alg in expected_korean_algs:
            alg_lower = korean_alg.lower()
            variations = korean_variations.get(alg_lower, [alg_lower])

            for variation in variations:
                if variation in actual_text:
                    found_count += 1
                    break

        return found_count / len(expected_korean_algs)

    @staticmethod
    def _calculate_findings_accuracy(actual_findings: Dict[str, Any], expected_findings: List[str]) -> float:
        if not expected_findings:
            return 1.0

        actual_text = json.dumps(actual_findings).lower()
        found_count = 0

        for expected in expected_findings:
            expected_lower = expected.lower()
            similarity_scores = []

            for key, value in actual_findings.items():
                value_str = str(value).lower()
                similarity = difflib.SequenceMatcher(None, expected_lower, value_str).ratio()
                similarity_scores.append(similarity)

            if similarity_scores and max(similarity_scores) > 0.6:
                found_count += 1

        return found_count / len(expected_findings) if expected_findings else 1.0

    @staticmethod
    def calculate_response_time_score(response_time: float, baseline: float = 10.0) -> float:
        if response_time <= baseline:
            return 1.0
        elif response_time <= baseline * 2:
            return 1.0 - (response_time - baseline) / baseline
        else:
            return 0.1

    @staticmethod
    def calculate_json_stability_score(response: Dict[str, Any]) -> float:
        if not response.get('valid_json', False):
            return 0.0

        analysis_results = response.get('analysis_results', {})
        has_confidence = 'confidence_score' in response
        has_summary = 'summary' in response and response['summary']

        stability_score = 0.6 if analysis_results else 0.0
        stability_score += 0.2 if has_confidence else 0.0
        stability_score += 0.2 if has_summary else 0.0

        return stability_score

    @staticmethod
    def calculate_completeness_score(response: Dict[str, Any], expected_points: List[str]) -> float:
        if not response.get('valid_json', False) or not expected_points:
            return 0.0

        analysis_results = response.get('analysis_results', {})
        if not analysis_results:
            return 0.0

        covered_points = 0
        total_points = len(expected_points)

        for point in expected_points:
            point_key = point.lower().replace(" ", "_").replace("-", "_")

            if point_key in analysis_results:
                covered_points += 1
            else:
                # Check for partial matches
                for key, value in analysis_results.items():
                    if point.lower() in key.lower() or point.lower() in str(value).lower():
                        covered_points += 1
                        break

        return covered_points / total_points if total_points > 0 else 0.0

    @staticmethod
    def calculate_false_positive_rate(actual_response: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Calculate false positive rate for vulnerable crypto detection"""
        if not ground_truth or not actual_response.get('valid_json'):
            return 1.0

        expected_findings = ground_truth.get('expected_findings', {})
        actual_findings = actual_response.get('analysis_results', {})

        # If no vulnerable algorithms are expected but some are detected, it's a false positive
        expected_algorithms = expected_findings.get('vulnerable_algorithms_detected', [])
        if not expected_algorithms:
            actual_text = json.dumps(actual_findings).lower()
            vulnerable_keywords = ['rsa', 'ecc', 'ecdsa', 'dsa', 'diffie-hellman', 'des', '3des',
                                 'rc4', 'md5', 'sha1', 'sha256', 'tea', 'salsa20', 'chacha20', 'poly1305',
                                 'hmac', 'crc32', 'seed', 'aria', 'hight', 'lea', 'trivium', 'vulnerable',
                                 'bls', 'boneh-lynn-shacham', 'blake2', 'ghash', 'pss', 'montgomery']

            false_positives = sum(1 for keyword in vulnerable_keywords if keyword in actual_text)
            return min(1.0, false_positives / len(vulnerable_keywords))

        return 0.0

    @staticmethod
    def calculate_false_negative_rate(actual_response: Dict[str, Any], ground_truth: Dict[str, Any]) -> float:
        """Calculate false negative rate for vulnerable crypto detection"""
        if not ground_truth or not actual_response.get('valid_json'):
            return 1.0

        expected_findings = ground_truth.get('expected_findings', {})
        actual_findings = actual_response.get('analysis_results', {})

        expected_algorithms = expected_findings.get('vulnerable_algorithms_detected', [])
        if not expected_algorithms:
            return 0.0

        actual_text = json.dumps(actual_findings).lower()
        missed_count = 0

        for algorithm in expected_algorithms:
            algorithm_lower = algorithm.lower()
            if algorithm_lower not in actual_text:
                # Check common variations
                variations = []
                if 'rsa' in algorithm_lower:
                    variations = ['rsa', 'rivest']
                elif 'ecc' in algorithm_lower or 'ecdsa' in algorithm_lower:
                    variations = ['ecc', 'ecdsa', 'elliptic']
                elif 'seed' in algorithm_lower:
                    variations = ['seed', 'korean']
                elif 'tea' in algorithm_lower:
                    variations = ['tea', 'tiny encryption']
                elif 'salsa20' in algorithm_lower:
                    variations = ['salsa20', 'salsa', 'stream']
                elif 'chacha20' in algorithm_lower:
                    variations = ['chacha20', 'chacha', 'stream']
                elif '3des' in algorithm_lower:
                    variations = ['3des', 'triple des', 'des']
                elif 'sha256' in algorithm_lower:
                    variations = ['sha256', 'sha-256', 'hash']
                elif 'aes' in algorithm_lower:
                    variations = ['aes', 'advanced encryption', 'rijndael']
                elif 'bls' in algorithm_lower:
                    variations = ['bls', 'boneh-lynn-shacham', 'signature aggregation']
                elif 'blake2' in algorithm_lower or 'blake' in algorithm_lower:
                    variations = ['blake2', 'blake', 'hash function']
                elif 'kyber' in algorithm_lower:
                    variations = ['kyber', 'kem', 'lattice-based']
                elif 'vdf' in algorithm_lower:
                    variations = ['vdf', 'verifiable delay', 'time-lock']
                elif 'ghash' in algorithm_lower:
                    variations = ['ghash', 'galois hash', 'gcm']
                elif 'pss' in algorithm_lower:
                    variations = ['pss', 'probabilistic signature']
                elif 'montgomery' in algorithm_lower:
                    variations = ['montgomery', 'modular arithmetic']

                found_variation = any(var in actual_text for var in variations)
                if not found_variation:
                    missed_count += 1

        return missed_count / len(expected_algorithms) if expected_algorithms else 0.0

    @staticmethod
    def aggregate_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not results:
            return {}

        total_tests = len(results)
        successful_tests = len([r for r in results if r.get('success', False)])

        accuracy_scores = [r.get('accuracy_score', 0.0) for r in results if r.get('success', False)]
        response_times = [r.get('response_time', 0.0) for r in results]
        json_scores = [r.get('json_stability_score', 0.0) for r in results]
        completeness_scores = [r.get('completeness_score', 0.0) for r in results if r.get('success', False)]
        false_positive_rates = [r.get('false_positive_rate', 0.0) for r in results if r.get('success', False)]
        false_negative_rates = [r.get('false_negative_rate', 0.0) for r in results if r.get('success', False)]

        return {
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'success_rate': successful_tests / total_tests if total_tests > 0 else 0.0,
            'average_vulnerable_crypto_detection_accuracy': sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0,
            'average_response_time': sum(response_times) / len(response_times) if response_times else 0.0,
            'average_json_stability': sum(json_scores) / len(json_scores) if json_scores else 0.0,
            'average_completeness': sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.0,
            'average_false_positive_rate': sum(false_positive_rates) / len(false_positive_rates) if false_positive_rates else 0.0,
            'average_false_negative_rate': sum(false_negative_rates) / len(false_negative_rates) if false_negative_rates else 0.0,
            'min_response_time': min(response_times) if response_times else 0.0,
            'max_response_time': max(response_times) if response_times else 0.0,
            'vulnerable_crypto_detection_precision': 1.0 - (sum(false_positive_rates) / len(false_positive_rates)) if false_positive_rates else 1.0,
            'vulnerable_crypto_detection_recall': 1.0 - (sum(false_negative_rates) / len(false_negative_rates)) if false_negative_rates else 1.0,
            'timestamp': datetime.now().isoformat()
        }